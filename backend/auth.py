"""Neon Auth integration for Flask application."""

import os
import json
import requests
from functools import wraps
from flask import request, session, redirect, url_for, flash, jsonify, make_response
from jose import jwt, JWTError
from datetime import datetime


# Neon Auth configuration
NEON_AUTH_URL = os.environ.get("NEON_AUTH_URL")
JWKS_URL = NEON_AUTH_URL + "/.well-known/jwks.json" if NEON_AUTH_URL else None
SESSION_COOKIE_NAME = "__Secure-neonauth.session_token"

# Cache for JWKS keys
_jwks_cache = None
_jwks_cache_time = None


def get_jwks():
    """Get JWKS keys from Neon Auth, with caching."""
    global _jwks_cache, _jwks_cache_time

    # Cache for 1 hour
    if _jwks_cache and _jwks_cache_time:
        if (datetime.now() - _jwks_cache_time).seconds < 3600:
            return _jwks_cache

    try:
        response = requests.get(JWKS_URL, timeout=5)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_time = datetime.now()
        return _jwks_cache
    except Exception as e:
        print("Error fetching JWKS: {}".format(e))
        return None


def verify_jwt_token(token):
    """Verify JWT token using JWKS."""
    if not token:
        return None

    try:
        # Get JWKS keys
        jwks = get_jwks()
        if not jwks:
            return None

        # Decode and verify token
        # jwt.decode will validate signature, expiration, etc.
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False},  # Neon Auth doesn't use audience claim
        )
        return payload
    except JWTError as e:
        print("JWT verification error: {}".format(e))
        return None
    except Exception as e:
        print("Error verifying JWT: {}".format(e))
        return None


def login_required(f):
    """Decorator to require Neon Auth authentication."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session with JWT token
        jwt_token = session.get("access_token")

        if jwt_token:
            # Verify JWT token
            payload = verify_jwt_token(jwt_token)
            if payload:
                # Store user info in request context
                request.user_id = payload.get("sub")
                request.user_email = payload.get("email")
                request.user_name = payload.get("email", "").split("@")[0]
                return f(*args, **kwargs)

        # Not authenticated
        if request.is_json or request.headers.get("Accept", "").startswith("application/json"):
            return jsonify({"ok": False, "message": "Not authenticated"}), 401
        else:
            return redirect(url_for("login"))

    return decorated_function


def get_current_user():
    """Get current user info from JWT token."""
    # Check request context first (from decorator)
    if hasattr(request, "user_id"):
        return {
            "id": request.user_id,
            "email": request.user_email,
            "name": request.user_name,
            "display_name": request.user_name,
            "initials": request.user_name[:2].upper() if request.user_name else "U",
        }

    # Try to verify JWT from session
    jwt_token = session.get("access_token")
    if jwt_token:
        payload = verify_jwt_token(jwt_token)
        if payload:
            user_name = payload.get("email", "").split("@")[0]
            return {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "name": user_name,
                "display_name": user_name,
                "initials": user_name[:2].upper() if user_name else "U",
            }

    return None


def login_user(email, password):
    """Log in a user with email and password via Neon Auth API."""
    if not NEON_AUTH_URL:
        print("NEON_AUTH_URL not configured")
        return False, "Authentication service not configured"

    try:
        # Call Neon Auth sign-in endpoint
        response = requests.post(
            NEON_AUTH_URL + "/sign-in/email",
            json={"email": email, "password": password},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()

            # Store JWT token in session
            if "session" in data and "access_token" in data["session"]:
                session["access_token"] = data["session"]["access_token"]
                session["user_email"] = email

                # Store user info if available
                if "user" in data:
                    session["user_id"] = data["user"].get("id")

                return True, None
            else:
                return False, "Invalid response from authentication service"
        else:
            error_msg = "Invalid email or password"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"]
            except:
                pass
            return False, error_msg

    except requests.exceptions.Timeout:
        return False, "Authentication service timeout"
    except Exception as e:
        print("Login error: {}".format(e))
        return False, "Authentication failed: {}".format(str(e))


def signup_user(email, password, name=None):
    """Sign up a new user via Neon Auth API."""
    if not NEON_AUTH_URL:
        print("NEON_AUTH_URL not configured")
        return False, "Authentication service not configured"

    try:
        # Call Neon Auth sign-up endpoint
        payload = {"email": email, "password": password}
        if name:
            payload["name"] = name

        response = requests.post(NEON_AUTH_URL + "/sign-up/email", json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Store JWT token in session if returned
            if "session" in data and "access_token" in data["session"]:
                session["access_token"] = data["session"]["access_token"]
                session["user_email"] = email

                # Store user info if available
                if "user" in data:
                    session["user_id"] = data["user"].get("id")

                return True, None
            else:
                # Some auth systems require email verification before session
                return True, "Account created. Please check your email to verify."

        else:
            error_msg = "Failed to create account"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"]
            except:
                pass
            return False, error_msg

    except requests.exceptions.Timeout:
        return False, "Authentication service timeout"
    except Exception as e:
        print("Signup error: {}".format(e))
        return False, "Signup failed: {}".format(str(e))


def logout_user():
    """Log out the current user."""
    session.pop("access_token", None)
    session.pop("user_email", None)
    session.pop("user_id", None)


def create_auth_urls():
    """Create authentication URLs for Neon Auth."""
    base_url = os.environ.get("BASE_URL", "http://localhost:5000")

    return {
        "login": "{}/login".format(base_url),
        "signup": "{}/signup".format(base_url),
        "callback": "{}/login".format(base_url),
        "logout": "{}/logout".format(base_url),
    }

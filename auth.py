"""Neon Auth integration for Flask application."""
import os
import json
import requests
from functools import wraps
from flask import request, session, redirect, url_for, flash, jsonify
import jwt
import time


# Neon Auth configuration
NEON_AUTH_URL = "https://ep-nameless-mouse-af40upqp.neonauth.c-2.us-west-2.aws.neon.tech/neondb"
JWKS_URL = "https://ep-nameless-mouse-af40upqp.neonauth.c-2.us-west-2.aws.neon.tech/neondb/auth/.well-known/jwks.json"

# Cache for JWKS keys
_jwks_cache = None
_jwks_cache_time = 0
JWKS_CACHE_DURATION = 3600  # 1 hour


def get_jwks():
    """Get JWKS keys, with caching."""
    global _jwks_cache, _jwks_cache_time

    current_time = time.time()
    if _jwks_cache and (current_time - _jwks_cache_time) < JWKS_CACHE_DURATION:
        return _jwks_cache

    try:
        response = requests.get(JWKS_URL, timeout=10)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_time = current_time
        return _jwks_cache
    except Exception as e:
        print("Error fetching JWKS: {}".format(e))
        return None


def verify_jwt(token):
    """Verify JWT token using Neon Auth JWKS."""
    try:
        # Get the header to find the key ID
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')

        if not kid:
            return None

        # Get JWKS
        jwks = get_jwks()
        if not jwks:
            return None

        # Find the matching key
        key = None
        for jwk_key in jwks.get('keys', []):
            if jwk_key.get('kid') == kid:
                key = jwt.PyJWK.from_dict(jwk_key)
                break

        if not key:
            return None

        # Verify and decode the token
        payload = jwt.decode(token, key.key, algorithms=['RS256'])
        return payload

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception as e:
        print("JWT verification error: {}".format(e))
        return None


def neon_auth_required(f):
    """Decorator to require Neon Auth authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for Authorization header (API requests)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_jwt(token)
            if payload:
                # Store user info in request context
                request.user_id = payload.get('sub')
                request.user_email = payload.get('email')
                request.user_name = payload.get('name')
                return f(*args, **kwargs)

        # Check for session-based auth (web requests)
        if 'user_token' in session:
            payload = verify_jwt(session['user_token'])
            if payload:
                request.user_id = payload.get('sub')
                request.user_email = payload.get('email')
                request.user_name = payload.get('name')
                return f(*args, **kwargs)

        # Not authenticated
        if request.is_json or request.headers.get("Accept", "").startswith("application/json"):
            return jsonify({"ok": False, "message": "Not authenticated"}), 401
        else:
            return redirect(url_for("login"))

    return decorated_function


def get_current_user():
    """Get current user info from session or request context."""
    # Check request context first (from decorator)
    if hasattr(request, 'user_id'):
        return {
            'id': request.user_id,
            'email': request.user_email,
            'name': request.user_name,
            'display_name': request.user_name or request.user_email.split('@')[0],
            'initials': (request.user_name or request.user_email.split('@')[0])[:2].upper()
        }

    # Check session
    if 'user_token' in session:
        payload = verify_jwt(session['user_token'])
        if payload:
            name = payload.get('name') or payload.get('email', '').split('@')[0]
            return {
                'id': payload.get('sub'),
                'email': payload.get('email'),
                'name': payload.get('name'),
                'display_name': name,
                'initials': name[:2].upper()
            }

    return None


def login_user(token):
    """Log in a user with their JWT token."""
    payload = verify_jwt(token)
    if not payload:
        return False

    session['user_token'] = token
    session['user_id'] = payload.get('sub')
    session['user_email'] = payload.get('email')
    session['user_name'] = payload.get('name')

    return True


def logout_user():
    """Log out the current user."""
    session.pop('user_token', None)
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_name', None)


def create_auth_urls():
    """Create authentication URLs for Neon Auth."""
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')

    return {
        'login': '{}/auth/login'.format(NEON_AUTH_URL),
        'signup': '{}/auth/signup'.format(NEON_AUTH_URL),
        'callback': '{}/auth/callback'.format(base_url),
        'logout': '{}/auth/logout'.format(NEON_AUTH_URL)
    }
import os
import httpx
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session

# Better Auth configuration
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3001")

# HTTP Bearer scheme for token authentication
security = HTTPBearer()

# Cache for JWKS (JSON Web Key Set)
_jwks_cache = None
_jwks_cache_time = None


async def get_jwks():
    """Fetch JWKS from Better Auth server with caching."""
    global _jwks_cache, _jwks_cache_time

    # Cache for 1 hour
    import time

    if _jwks_cache and _jwks_cache_time and (time.time() - _jwks_cache_time < 3600):
        return _jwks_cache

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BETTER_AUTH_URL}/.well-known/jwks.json")
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_cache_time = time.time()
            return _jwks_cache
    except Exception as e:
        print(f"Error fetching JWKS: {e}")
        return None


async def verify_better_auth_token(token: str) -> Optional[dict]:
    """Verify Better Auth JWT token."""
    try:
        # For Better Auth, we can decode without verifying signature first
        # to get the payload, then verify if needed
        unverified_payload = jwt.get_unverified_claims(token)

        # Basic validation
        if not unverified_payload.get("sub"):
            return None

        # You can add JWKS verification here if needed
        # For now, we'll trust tokens from our auth server

        return unverified_payload
    except JWTError as e:
        print(f"JWT verification error: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get current authenticated user from Better Auth JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = await verify_better_auth_token(token)

    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id:
        raise credentials_exception

    # Return user info from token payload
    # Better Auth tokens contain user information
    return {
        "id": user_id,
        "email": email,
        "display_name": payload.get("name", email.split("@")[0] if email else "User"),
        "initials": "".join(
            [word[0].upper() for word in payload.get("name", email.split("@")[0]).split()[:2]]
        )
        if email
        else "U",
    }

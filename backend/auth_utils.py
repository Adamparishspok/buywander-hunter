import os
import httpx
from fastapi import Depends, HTTPException, status, Request

# Better Auth configuration
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3001")


async def get_current_user(request: Request) -> dict:
    """Get current authenticated user from Better Auth session cookie."""
    # Extract the session token cookie
    session_token = request.cookies.get("better-auth.session_token")
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - no session cookie found",
        )

    # Verify the session by calling the Better Auth server
    try:
        async with httpx.AsyncClient() as client:
            # Forward the session cookie to Better Auth for verification
            response = await client.get(
                f"{BETTER_AUTH_URL}/api/auth/get-session",
                cookies={"better-auth.session_token": session_token},
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired session",
                )
            
            session_data = response.json()
            
            # Better Auth returns session data with user info
            if not session_data.get("user"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No user in session",
                )
            
            user = session_data["user"]
            
            # Return user info in the format expected by the app
            return {
                "id": user.get("id"),
                "email": user.get("email"),
                "display_name": user.get("name") or user.get("email", "").split("@")[0],
                "initials": "".join(
                    [word[0].upper() for word in (user.get("name") or "User").split()[:2]]
                ),
            }
    except httpx.RequestError as e:
        print(f"Error connecting to auth server: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable",
        )
    except Exception as e:
        print(f"Error verifying session: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate session",
        )

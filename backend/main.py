import asyncio
import json
import os
import threading
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import get_session, init_db
from models import (
    ScrapeHistory,
    ScrapeItem,
    ScrapeHistoryResponse,
    ScrapeItemResponse,
    InterestCreate,
    ScheduleUpdate,
)
from auth_utils import get_current_user
import scraper

# File paths for JSON-based data (temporary until migrated to DB)
INTERESTS_FILE = "interests.json"
SCRAPE_STATE_FILE = "scrape_state.json"
SCHEDULE_FILE = "schedule.json"

# Scheduler
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    await init_db()
    scheduler.start()

    # Load and set schedule
    schedule_config = load_schedule()
    save_schedule(schedule_config)

    # Startup cleanup
    threading.Thread(target=startup_cleanup, daemon=True).start()

    yield

    # Shutdown
    scheduler.shutdown()


app = FastAPI(
    title="BuyWander Deal Hunter API",
    description="FastAPI backend for BuyWander deal tracking",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Helper Functions ====================


def load_scrape_state(user_id: Optional[int] = None) -> dict:
    """Load current scrape state from disk."""
    if os.path.exists(SCRAPE_STATE_FILE):
        try:
            with open(SCRAPE_STATE_FILE, "r") as f:
                all_states = json.load(f)
                if user_id:
                    return all_states.get(
                        str(user_id),
                        {"running": False, "message": "", "items_found": 0, "pull_id": None},
                    )
                return all_states
        except Exception:
            pass
    return {"running": False, "message": "", "items_found": 0, "pull_id": None}


def save_scrape_state(state: dict, user_id: Optional[int] = None):
    """Persist scrape state to disk."""
    try:
        all_states = {}
        if os.path.exists(SCRAPE_STATE_FILE):
            try:
                with open(SCRAPE_STATE_FILE, "r") as f:
                    all_states = json.load(f)
            except Exception:
                pass

        if user_id:
            all_states[str(user_id)] = state
            with open(SCRAPE_STATE_FILE, "w") as f:
                json.dump(all_states, f)
    except Exception as e:
        print(f"Error saving scrape state: {e}")


def load_interests(username: Optional[str] = None) -> dict:
    """Load interests from JSON file."""
    if os.path.exists(INTERESTS_FILE):
        try:
            with open(INTERESTS_FILE, "r") as f:
                all_interests = json.load(f)
                if username:
                    return all_interests.get(username, {})
                return all_interests
        except Exception as e:
            print(f"Error loading interests: {e}")
    return {}


def save_interests(interests: dict, username: Optional[str] = None) -> bool:
    """Save interests to JSON file."""
    try:
        all_interests = {}
        if os.path.exists(INTERESTS_FILE):
            try:
                with open(INTERESTS_FILE, "r") as f:
                    all_interests = json.load(f)
            except Exception:
                pass

        if username:
            all_interests[username] = interests
        else:
            all_interests = interests

        with open(INTERESTS_FILE, "w") as f:
            json.dump(all_interests, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving interests: {e}")
        return False


def load_schedule() -> dict:
    """Load schedule configuration."""
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"enabled": False}


def save_schedule(config: dict) -> bool:
    """Save schedule configuration and update scheduler."""
    try:
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(config, f)

        scheduler.remove_all_jobs()

        # Always schedule cleanup job
        scheduler.add_job(
            func=scheduled_cleanup_job,
            trigger="cron",
            hour=2,
            minute=0,
            id="daily_cleanup",
            replace_existing=True,
        )
        print("Scheduled daily cleanup for 2:00 AM.")

        if config.get("enabled"):
            scheduler.add_job(
                func=scheduled_scrape_job,
                trigger="cron",
                hour=18,
                minute=0,
                id="nightly_scrape",
                replace_existing=True,
            )
            print("Scheduled nightly scrape for 6:00 PM.")
        else:
            print("Nightly scrape disabled.")

        return True
    except Exception as e:
        print(f"Error saving schedule: {e}")
        return False


def startup_cleanup():
    """Run cleanup on startup to remove old data."""
    try:
        from db import cleanup_old_scrapes

        result = cleanup_old_scrapes(days_old=2)
        print(f"Startup cleanup completed: deleted {result['history_deleted']} history entries")
    except Exception as e:
        print(f"Error during startup cleanup: {e}")


def scheduled_cleanup_job():
    """Scheduled job to clean up old data."""
    print("Running scheduled cleanup of old scrape data...")
    try:
        from db import cleanup_old_scrapes

        result = cleanup_old_scrapes(days_old=2)
        print(f"Cleanup completed: deleted {result['history_deleted']} entries")
    except Exception as e:
        print(f"Error during cleanup: {e}")


def scheduled_scrape_job():
    """Scheduled job to run scraper."""
    print("Running scheduled nightly scrape...")
    # Implementation would iterate over users and run scraper
    # For now, keeping it simple


async def run_scraper_task(pull_id: str, user_id: int, user_interests: dict):
    """Background task that runs the scraper."""
    try:
        state = load_scrape_state(user_id=user_id)
        state["message"] = "Fetching auctions from BuyWander..."
        save_scrape_state(state, user_id=user_id)
        print(f"Starting scraper for pull {pull_id}...")

        items = scraper.monitor_deals(interests=user_interests)
        items_count = len(items)
        print(f"Scraper done. Found {items_count} items for pull {pull_id}.")

        # Save to database
        from db import save_pull_history, save_pull_items

        timestamp = datetime.now()
        save_pull_history(pull_id, timestamp, "success", items_count, user_id=user_id)
        if items:
            save_pull_items(pull_id, items)

        state = load_scrape_state(user_id=user_id)
        state["message"] = f"Done! Found {items_count} products."
        state["items_found"] = items_count
        state["running"] = False
        save_scrape_state(state, user_id=user_id)
    except Exception as e:
        print(f"Error in scraper: {e}")
        import traceback

        traceback.print_exc()

        from db import save_pull_history

        timestamp = datetime.now()
        save_pull_history(pull_id, timestamp, "error", 0, str(e), user_id=user_id)

        state = load_scrape_state(user_id=user_id)
        state["message"] = f"Error: {e}"
        state["running"] = False
        save_scrape_state(state, user_id=user_id)


# ==================== Auth Routes ====================
# Auth is handled by Better Auth server on port 3001
# FastAPI only verifies tokens and returns user info


@app.get("/api/auth/me", response_model=dict)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info from Better Auth token."""
    return {"success": True, "user": current_user}


@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_auth(path: str, request: Request):
    """Proxy requests to the Better Auth server."""
    better_auth_url = os.getenv("BETTER_AUTH_URL", "http://localhost:3001")
    # Ensure no trailing slash on base URL
    better_auth_url = better_auth_url.rstrip("/")
    
    target_url = f"{better_auth_url}/api/auth/{path}"
    
    # Forward query params
    params = dict(request.query_params)
    
    # Forward headers (excluding host to avoid issues)
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None) # Let httpx handle this
    
    # Forward body
    body = await request.body()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                params=params,
                headers=headers,
                content=body,
                follow_redirects=False
            )
        except httpx.RequestError as e:
            print(f"Auth proxy error: {e}")
            raise HTTPException(status_code=502, detail="Auth server unavailable")
        
    # Create response
    proxy_response = Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
    return proxy_response


# ==================== Scraping Routes ====================


@app.post("/api/scrape")
async def start_scrape(
    current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    """Start a scrape job."""
    user_id = current_user.id

    state = load_scrape_state(user_id=user_id)
    if state.get("running"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="A pull is already in progress"
        )

    pull_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_interests = load_interests(username=current_user.email)

    state = {
        "running": True,
        "message": "Starting...",
        "items_found": 0,
        "pull_id": pull_id,
    }
    save_scrape_state(state, user_id=user_id)

    # Start background thread
    thread = threading.Thread(
        target=lambda: asyncio.run(run_scraper_task(pull_id, user_id, user_interests)), daemon=True
    )
    thread.start()

    return {"success": True, "message": "Pull started"}


@app.get("/api/scrape/status")
async def get_scrape_status(current_user: User = Depends(get_current_user)):
    """Get scrape job status."""
    user_id = current_user.id
    state = load_scrape_state(user_id=user_id)
    return {"success": True, "status": state}


@app.get("/api/history")
async def get_history(
    current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    """Get scrape history."""
    try:
        from db import load_history

        scrape_history = load_history(user_id=current_user.id)

        # Convert datetime to strings
        for entry in scrape_history:
            if "timestamp" in entry and isinstance(entry["timestamp"], datetime):
                entry["timestamp"] = entry["timestamp"].isoformat()

        return {"success": True, "history": scrape_history}
    except Exception as e:
        print(f"Error loading history: {e}")
        raise HTTPException(status_code=500, detail="Error loading history")


# ==================== Settings Routes ====================


@app.get("/api/settings")
async def get_settings(current_user: User = Depends(get_current_user)):
    """Get user settings."""
    interests = load_interests(username=current_user.email)
    schedule = load_schedule()

    return {"success": True, "settings": {"interests": interests, "schedule": schedule}}


@app.post("/api/settings/schedule")
async def update_schedule_endpoint(
    schedule_data: ScheduleUpdate, current_user: User = Depends(get_current_user)
):
    """Update schedule settings."""
    config = {"enabled": schedule_data.enabled}

    if save_schedule(config):
        status_text = "enabled" if schedule_data.enabled else "disabled"
        return {"success": True, "message": f"Nightly scan {status_text}"}
    else:
        raise HTTPException(status_code=500, detail="Error saving schedule settings")


@app.post("/api/settings/interests")
async def add_interest_endpoint(
    interest_data: InterestCreate, current_user: User = Depends(get_current_user)
):
    """Add an interest category."""
    username = current_user.email

    if not interest_data.category or not interest_data.keywords:
        raise HTTPException(status_code=400, detail="Category and keywords are required")

    keywords = [k.strip() for k in interest_data.keywords.split(",") if k.strip()]
    interests = load_interests(username=username)
    interests[interest_data.category] = keywords

    if save_interests(interests, username=username):
        return {"success": True, "message": f"Added interest category: {interest_data.category}"}
    else:
        raise HTTPException(status_code=500, detail="Error saving interest")


@app.delete("/api/settings/interests/{category}")
async def delete_interest_endpoint(category: str, current_user: User = Depends(get_current_user)):
    """Delete an interest category."""
    username = current_user.email
    interests = load_interests(username=username)

    if category in interests:
        del interests[category]
        if save_interests(interests, username=username):
            return {"success": True, "message": f"Deleted interest category: {category}"}
        else:
            raise HTTPException(status_code=500, detail="Error saving changes")
    else:
        raise HTTPException(status_code=404, detail="Category not found")


# ==================== Data Routes ====================


@app.get("/api/pull/{pull_id}")
async def get_pull_detail(
    pull_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get details of a specific pull."""
    try:
        from db import load_pull_items, load_history

        deals = load_pull_items(pull_id)
        history = load_history(user_id=current_user.id)
        entry = next((e for e in history if e.get("pull_id") == pull_id), None)

        pull_name = entry["timestamp"].isoformat() if entry and "timestamp" in entry else pull_id
        categories = sorted(list(set(d.get("Interest Category", "Unknown") for d in deals)))

        return {
            "success": True,
            "pull": {
                "pull_id": pull_id,
                "pull_name": pull_name,
                "deals": deals,
                "total_items": len(deals),
                "categories": categories,
            },
        }
    except Exception as e:
        print(f"Error loading pull {pull_id}: {e}")
        raise HTTPException(status_code=500, detail="Error loading pull data")


@app.post("/api/cleanup")
async def manual_cleanup(current_user: User = Depends(get_current_user)):
    """Manually trigger cleanup of old data."""
    try:
        from db import cleanup_old_scrapes

        result = cleanup_old_scrapes(days_old=2)
        message = (
            f"Cleanup completed: deleted {result['history_deleted']} history entries "
            f"and {result['items_deleted']} items older than {result['days_old']} days"
        )
        print(message)
        return {"success": True, "message": message, "result": result}
    except Exception as e:
        error_msg = f"Cleanup failed: {e}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


# ==================== Health Check ====================


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "buywander-api"}


# ==================== Static Files (Frontend) ====================

# Mount assets directory if it exists (for CSS/JS)
if os.path.exists("static/assets"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# Serve other static files (favicon, etc.) and index.html for SPA
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve the Vue frontend for any unknown routes (SPA)."""
    # Allow API routes to pass through (should be handled above, but just in case)
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    # Check if a specific static file exists
    file_path = os.path.join("static", full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    # Otherwise return index.html for Vue Router to handle
    index_path = "static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # Fallback if static files aren't built/copied
    raise HTTPException(status_code=404, detail="Frontend not found (static files missing)")


if __name__ == "__main__":
    import uvicorn
    import asyncio

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")

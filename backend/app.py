import hashlib
import json
import os
import threading
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request, session
from flask_cors import CORS

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import scraper
import db
import auth
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# Enable CORS for frontend
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://localhost:3000"])

# --- File paths (for things still in JSON) ---
INTERESTS_FILE = "interests.json"
USERS_FILE = "users.json"
SCRAPE_STATE_FILE = "scrape_state.json"
SCHEDULE_FILE = "schedule.json"


# --- Scheduler ---
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


def scheduled_scrape_job():
    """Job to run the scraper on schedule."""
    print("Running scheduled nightly scrape...")

    users = load_users()
    for username in users:
        print("Starting scheduled scrape for {}...".format(username))
        pull_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_{}".format(username)

        state = load_scrape_state(username=username)
        if state.get("running"):
            print("Skipping scheduled scrape for {}: Scraper already running.".format(username))
            continue

        state = {
            "running": True,
            "message": "Starting scheduled scrape...",
            "items_found": 0,
            "pull_id": pull_id,
        }
        save_scrape_state(state, username=username)

        user_interests = load_interests(username=username)
        _run_scraper_task(pull_id, username=username, user_interests=user_interests)


def scheduled_cleanup_job():
    """Job to clean up old scrape data (older than 2 days)."""
    print("Running scheduled cleanup of old scrape data...")
    try:
        import db

        result = db.cleanup_old_scrapes(days_old=2)
        print(
            "Cleanup completed: deleted {} history entries and {} items older than {} days".format(
                result["history_deleted"], result["items_deleted"], result["days_old"]
            )
        )
    except Exception as e:
        print("Error during cleanup: {}".format(e))


def load_schedule():
    """Load schedule configuration."""
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"enabled": False}


def save_schedule(config):
    """Save schedule configuration and update scheduler."""
    try:
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(config, f)

        scheduler.remove_all_jobs()

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
        print("Error saving schedule: {}".format(e))
        return False


# Initialize schedule on startup
save_schedule(load_schedule())


# Run initial cleanup on startup (in background)
def startup_cleanup():
    """Run cleanup on startup to remove any existing old data."""
    try:
        import db

        result = db.cleanup_old_scrapes(days_old=2)
        print(
            "Startup cleanup completed: deleted {} history entries and {} items".format(
                result["history_deleted"], result["items_deleted"]
            )
        )
    except Exception as e:
        print("Error during startup cleanup: {}".format(e))


cleanup_thread = threading.Thread(target=startup_cleanup, daemon=True)
cleanup_thread.start()


# --- Scrape state (file-based, survives restarts) ---
def load_scrape_state(user_id=None):
    """Load current scrape state from disk."""
    if os.path.exists(SCRAPE_STATE_FILE):
        try:
            with open(SCRAPE_STATE_FILE, "r") as f:
                all_states = json.load(f)
                if user_id:
                    return all_states.get(
                        user_id,
                        {"running": False, "message": "", "items_found": 0, "pull_id": None},
                    )
                return all_states
        except Exception:
            pass
    return {"running": False, "message": "", "items_found": 0, "pull_id": None}


def save_scrape_state(state, user_id=None):
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
            all_states[user_id] = state
            with open(SCRAPE_STATE_FILE, "w") as f:
                json.dump(all_states, f)
    except Exception as e:
        print("Error saving scrape state: {}".format(e))


# On startup: if state says "running" but no thread is alive, mark it failed
if os.path.exists(SCRAPE_STATE_FILE):
    try:
        with open(SCRAPE_STATE_FILE, "r") as f:
            _all_states = json.load(f)
            _updated = False
            for _user, _state in _all_states.items():
                if isinstance(_state, dict) and _state.get("running"):
                    print(
                        "Previous scrape for {} was interrupted. Marking as failed.".format(_user)
                    )
                    _state["running"] = False
                    _state["message"] = "Interrupted by server restart"
                    _updated = True

            if _updated:
                with open(SCRAPE_STATE_FILE, "w") as f:
                    json.dump(_all_states, f)
    except Exception:
        pass


# --- Auth helpers ---
login_required = auth.login_required


# --- User helpers (still JSON-based) ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Error loading users: {}".format(e))

    default_users = {
        "Adam": {
            "password": hash_password("adam123"),
            "display_name": "Adam",
            "initials": "AP",
        },
        "Alex": {
            "password": hash_password("alex123"),
            "display_name": "Alex",
            "initials": "AP",
        },
    }
    save_users(default_users)
    return default_users


def save_users(users):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)
        return True
    except Exception as e:
        print("Error saving users: {}".format(e))
        return False


def verify_user(username, password):
    users = load_users()
    if username in users:
        return hash_password(password) == users[username]["password"]
    return False


# --- Interest helpers (still JSON-based) ---
def load_interests(username=None):
    if os.path.exists(INTERESTS_FILE):
        try:
            with open(INTERESTS_FILE, "r") as f:
                all_interests = json.load(f)
                if username:
                    return all_interests.get(username, {})
                return all_interests
        except Exception as e:
            print("Error loading interests: {}".format(e))
    return {}


def save_interests(interests, username=None):
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
        print("Error saving interests: {}".format(e))
        return False


# --- API Routes ---
@app.route("/api/auth/login", methods=["POST"])
def login():
    """Handle Neon Auth login."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    success, error = auth.login_user(email, password)
    if success:
        user = auth.get_current_user()
        if user:
            return jsonify({"success": True, "message": "Login successful", "user": user})

    return jsonify({"success": False, "message": error or "Invalid email or password"}), 401


@app.route("/api/auth/signup", methods=["POST"])
def signup():
    """Handle Neon Auth signup."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    success, error = auth.signup_user(email, password, name)
    if success:
        if error:
            return jsonify({"success": True, "message": error, "requiresVerification": True})
        else:
            user = auth.get_current_user()
            if user:
                return jsonify(
                    {"success": True, "message": "Account created successfully", "user": user}
                )

    return jsonify({"success": False, "message": error or "Failed to create account"}), 400


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """Handle logout."""
    auth.logout_user()
    return jsonify({"success": True, "message": "Logged out successfully"})


@app.route("/api/auth/me", methods=["GET"])
@login_required
def get_me():
    """Get current user info."""
    user = auth.get_current_user()
    if user:
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "message": "Not authenticated"}), 401


@app.route("/api/history", methods=["GET"])
@login_required
def get_history():
    """Get scrape history."""
    user = auth.get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    try:
        user_id = user.get("id")
        scrape_history = db.load_history(user_id=user_id)
        # Convert datetime objects to strings
        for entry in scrape_history:
            if "timestamp" in entry and isinstance(entry["timestamp"], datetime):
                entry["timestamp"] = entry["timestamp"].isoformat()
        return jsonify({"success": True, "history": scrape_history})
    except Exception as e:
        print("Error loading history from DB: {}".format(e))
        return jsonify({"success": False, "message": "Error loading history"}), 500


# --- Scraper background task ---
def _run_scraper_task(pull_id, user_id=None, user_interests=None):
    """Background task that runs the scraper and saves to database."""
    try:
        state = load_scrape_state(user_id=user_id)
        state["message"] = "Fetching auctions from BuyWander..."
        save_scrape_state(state, user_id=user_id)
        print("Starting scraper for pull {}...".format(pull_id))

        items = scraper.monitor_deals(interests=user_interests)

        items_count = len(items)
        print("Scraper done. Found {} items for pull {}.".format(items_count, pull_id))

        timestamp = datetime.now()
        db.save_pull_history(pull_id, timestamp, "success", items_count, user_id=user_id)
        if items:
            db.save_pull_items(pull_id, items)

        state = load_scrape_state(user_id=user_id)
        state["message"] = "Done! Found {} products.".format(items_count)
        state["items_found"] = items_count
        state["running"] = False
        save_scrape_state(state, user_id=user_id)
    except Exception as e:
        print("Error in scraper: {}".format(e))
        import traceback

        traceback.print_exc()

        timestamp = datetime.now()
        db.save_pull_history(pull_id, timestamp, "error", 0, str(e), user_id=user_id)

        state = load_scrape_state(user_id=user_id)
        state["message"] = "Error: {}".format(e)
        state["running"] = False
        save_scrape_state(state, user_id=user_id)


@app.route("/api/scrape", methods=["POST"])
@login_required
def run_scraper():
    """Start a scrape."""
    user = auth.get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    user_id = user.get("id")

    state = load_scrape_state(user_id=user_id)
    if state.get("running"):
        return jsonify({"success": False, "message": "A pull is already in progress"}), 409

    pull_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_interests = load_interests(username=user.get("email", ""))

    state = {
        "running": True,
        "message": "Starting...",
        "items_found": 0,
        "pull_id": pull_id,
    }
    save_scrape_state(state, user_id=user_id)

    thread = threading.Thread(
        target=_run_scraper_task, args=(pull_id, user_id, user_interests), daemon=True
    )
    thread.start()

    return jsonify({"success": True, "message": "Pull started"})


@app.route("/api/scrape/status", methods=["GET"])
@login_required
def scrape_progress():
    """Get scrape progress."""
    user = auth.get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    user_id = user.get("id")
    state = load_scrape_state(user_id=user_id)
    return jsonify({"success": True, "status": state})


@app.route("/api/cleanup", methods=["POST"])
@login_required
def manual_cleanup():
    """Manually trigger cleanup of old scrape data."""
    user = auth.get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    try:
        result = db.cleanup_old_scrapes(days_old=2)
        message = (
            "Cleanup completed: deleted {} history entries and {} items older than {} days".format(
                result["history_deleted"], result["items_deleted"], result["days_old"]
            )
        )
        print(message)
        return jsonify({"success": True, "message": message, "result": result})
    except Exception as e:
        error_msg = "Cleanup failed: {}".format(e)
        print(error_msg)
        return jsonify({"success": False, "message": error_msg}), 500


# --- Settings API ---
@app.route("/api/settings", methods=["GET"])
@login_required
def get_settings():
    """Get settings."""
    user = auth.get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    interests = load_interests(username=user.get("email", ""))
    schedule = load_schedule()

    return jsonify({"success": True, "settings": {"interests": interests, "schedule": schedule}})


@app.route("/api/settings/schedule", methods=["POST"])
@login_required
def update_schedule():
    """Update schedule settings."""
    user = auth.get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    data = request.get_json()
    enabled = data.get("enabled", False)

    config = {"enabled": enabled}
    if save_schedule(config):
        status = "enabled" if enabled else "disabled"
        return jsonify({"success": True, "message": "Nightly scan {}".format(status)})
    else:
        return jsonify({"success": False, "message": "Error saving schedule settings"}), 500


@app.route("/api/settings/interests", methods=["POST"])
@login_required
def add_interest():
    """Add an interest category."""
    user = auth.get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    data = request.get_json()
    category = data.get("category")
    keywords_str = data.get("keywords")
    username = user.get("email", "")

    if not category or not keywords_str:
        return jsonify({"success": False, "message": "Category and keywords are required"}), 400

    keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
    interests = load_interests(username=username)
    interests[category] = keywords

    if save_interests(interests, username=username):
        return jsonify({"success": True, "message": "Added interest category: {}".format(category)})
    else:
        return jsonify({"success": False, "message": "Error saving interest"}), 500


@app.route("/api/settings/interests/<category>", methods=["DELETE"])
@login_required
def delete_interest(category):
    """Delete an interest category."""
    user = auth.get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    username = user.get("email", "")
    interests = load_interests(username=username)

    if category in interests:
        del interests[category]
        if save_interests(interests, username=username):
            return jsonify(
                {"success": True, "message": "Deleted interest category: {}".format(category)}
            )
        else:
            return jsonify({"success": False, "message": "Error saving changes"}), 500
    else:
        return jsonify({"success": False, "message": "Category not found"}), 404


@app.route("/api/pull/<pull_id>", methods=["GET"])
@login_required
def pull_detail(pull_id):
    """Get data from a specific pull."""
    user = auth.get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    user_id = user.get("id")

    try:
        deals = db.load_pull_items(pull_id)
        history = db.load_history(user_id=user_id)
        entry = next((e for e in history if e.get("pull_id") == pull_id), None)

        pull_name = entry["timestamp"].isoformat() if entry and "timestamp" in entry else pull_id
        categories = sorted(list(set(d.get("Interest Category", "Unknown") for d in deals)))

        return jsonify(
            {
                "success": True,
                "pull": {
                    "pull_id": pull_id,
                    "pull_name": pull_name,
                    "deals": deals,
                    "total_items": len(deals),
                    "categories": categories,
                },
            }
        )
    except Exception as e:
        print("Error loading pull {}: {}".format(pull_id, e))
        return jsonify({"success": False, "message": "Error loading pull data"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

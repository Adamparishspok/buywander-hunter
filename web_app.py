import hashlib
import json
import os
import threading
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without .env loading
    pass

import scraper
import db
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

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
    
    # Iterate over all users and run scrape for each
    users = load_users()
    for username in users:
        print("Starting scheduled scrape for {}...".format(username))
        # Create a unique pull ID
        pull_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_{}".format(username)
        
        # Check if already running for this user
        state = load_scrape_state(username=username)
        if state.get("running"):
            print("Skipping scheduled scrape for {}: Scraper already running.".format(username))
            continue

        # Set state
        state = {
            "running": True,
            "message": "Starting scheduled scrape...",
            "items_found": 0,
            "pull_id": pull_id,
        }
        save_scrape_state(state, username=username)
        
        # Load user interests
        user_interests = load_interests(username=username)
        
        # Run task directly (we are already in a background thread from scheduler)
        # Note: This runs sequentially for each user. If we have many users, we might want to thread this.
        # But for 2 users, it's fine.
        _run_scraper_task(pull_id, username=username, user_interests=user_interests)


def scheduled_cleanup_job():
    """Job to clean up old scrape data (older than 2 days)."""
    print("Running scheduled cleanup of old scrape data...")
    try:
        import db
        result = db.cleanup_old_scrapes(days_old=2)
        print("Cleanup completed: deleted {} history entries and {} items older than {} days".format(
            result["history_deleted"], result["items_deleted"], result["days_old"]
        ))
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
        
        # Update scheduler
        scheduler.remove_all_jobs()

        # Always schedule cleanup job (daily at 2:00 AM)
        scheduler.add_job(
            func=scheduled_cleanup_job,
            trigger="cron",
            hour=2,
            minute=0,
            id="daily_cleanup",
            replace_existing=True
        )
        print("Scheduled daily cleanup for 2:00 AM.")

        if config.get("enabled"):
            # Schedule for 6:00 PM (18:00) daily
            scheduler.add_job(
                func=scheduled_scrape_job,
                trigger="cron",
                hour=18,
                minute=0,
                id="nightly_scrape",
                replace_existing=True
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
        print("Startup cleanup completed: deleted {} history entries and {} items".format(
            result["history_deleted"], result["items_deleted"]
        ))
    except Exception as e:
        print("Error during startup cleanup: {}".format(e))

# Run cleanup in background thread to avoid blocking startup
import threading
cleanup_thread = threading.Thread(target=startup_cleanup, daemon=True)
cleanup_thread.start()


# --- Scrape state (file-based, survives restarts) ---
def load_scrape_state(username=None):
    """Load current scrape state from disk."""
    if os.path.exists(SCRAPE_STATE_FILE):
        try:
            with open(SCRAPE_STATE_FILE, "r") as f:
                all_states = json.load(f)
                if username:
                    return all_states.get(username, {"running": False, "message": "", "items_found": 0, "pull_id": None})
                return all_states
        except Exception:
            pass
    return {"running": False, "message": "", "items_found": 0, "pull_id": None}


def save_scrape_state(state, username=None):
    """Persist scrape state to disk."""
    try:
        all_states = {}
        if os.path.exists(SCRAPE_STATE_FILE):
            try:
                with open(SCRAPE_STATE_FILE, "r") as f:
                    all_states = json.load(f)
            except Exception:
                pass
        
        if username:
            all_states[username] = state
            with open(SCRAPE_STATE_FILE, "w") as f:
                json.dump(all_states, f)
    except Exception as e:
        print("Error saving scrape state: {}".format(e))


# On startup: if state says "running" but no thread is alive, mark it failed
_startup_states = load_scrape_state()
if isinstance(_startup_states, dict):
    # It returns all states if no username passed, but load_scrape_state returns a default dict if file missing
    # If it returns the default dict (which has "running" key), it means file was missing or empty or old format.
    # But now load_scrape_state returns all_states (dict of users) if no username passed.
    # Wait, my implementation of load_scrape_state returns all_states which is a dict of dicts.
    # But if file doesn't exist, it returns a single state dict. This is inconsistent.
    pass

# Let's fix load_scrape_state behavior for no username first.
# If username is None, it should return the whole dict of users -> states.
# If file missing, return empty dict.
# My previous edit:
# if username: return all_states.get(username, default)
# return all_states
# This is correct.

# So back to startup check:
if os.path.exists(SCRAPE_STATE_FILE):
    try:
        with open(SCRAPE_STATE_FILE, "r") as f:
            _all_states = json.load(f)
            _updated = False
            for _user, _state in _all_states.items():
                if isinstance(_state, dict) and _state.get("running"):
                    print("Previous scrape for {} was interrupted. Marking as failed.".format(_user))
                    _state["running"] = False
                    _state["message"] = "Interrupted by server restart"
                    _updated = True
            
            if _updated:
                with open(SCRAPE_STATE_FILE, "w") as f:
                    json.dump(_all_states, f)
    except Exception:
        pass


# --- Auth helpers ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            if request.is_json or request.headers.get("Accept", "").startswith(
                "application/json"
            ):
                return jsonify({"ok": False, "message": "Not logged in"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


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
            # If no username provided, assume we are saving the whole dict (legacy or admin)
            # But for safety, let's just require username for updates or handle it carefully.
            # In this app context, we only call save_interests with user data.
            # If interests is a dict of users, we save it as is.
            all_interests = interests

        with open(INTERESTS_FILE, "w") as f:
            json.dump(all_interests, f, indent=4)
        return True
    except Exception as e:
        print("Error saving interests: {}".format(e))
        return False


def get_user_info():
    return {
        "display_name": session.get("display_name", "User"),
        "initials": session.get("initials", "U"),
    }


# --- Routes ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if verify_user(username, password):
            session["logged_in"] = True
            session["username"] = username
            users = load_users()
            session["display_name"] = users[username]["display_name"]
            session["initials"] = users[username]["initials"]
            flash('Welcome back, {}!'.format(session["display_name"]), "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("username", None)
    session.pop("display_name", None)
    session.pop("initials", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    try:
        scrape_history = db.load_history(user_id=session.get("username"))
    except Exception as e:
        print("Error loading history from DB: {}".format(e))
        scrape_history = []
        flash("Error loading history from database.", "error")
    
    return render_template(
        "index.html", history=scrape_history, user=get_user_info()
    )


# --- Scraper background task ---
def _run_scraper_task(pull_id, username=None, user_interests=None):
    """Background task that runs the scraper and saves to database."""
    try:
        state = load_scrape_state(username=username)
        state["message"] = "Fetching auctions from BuyWander..."
        save_scrape_state(state, username=username)
        print("Starting scraper for pull {}...".format(pull_id))

        # Run the scraper - it returns a list of items
        # If user_interests is provided, use it. Otherwise, scraper might load default (or we should pass empty)
        items = scraper.monitor_deals(interests=user_interests)

        items_count = len(items)
        print("Scraper done. Found {} items for pull {}.".format(items_count, pull_id))

        # Save to database
        timestamp = datetime.now().strftime("%b %d, %Y - %I:%M %p")
        db.save_pull_history(pull_id, timestamp, "success", items_count, user_id=username)
        if items:
            db.save_pull_items(pull_id, items)

        state = load_scrape_state(username=username)
        state["message"] = "Done! Found {} products.".format(items_count)
        state["items_found"] = items_count
        state["running"] = False
        save_scrape_state(state, username=username)
    except Exception as e:
        print("Error in scraper: {}".format(e))
        import traceback
        traceback.print_exc()

        timestamp = datetime.now().strftime("%b %d, %Y - %I:%M %p")
        db.save_pull_history(pull_id, timestamp, "error", 0, str(e), user_id=username)

        state = load_scrape_state(username=username)
        state["message"] = "Error: {}".format(e)
        state["running"] = False
        save_scrape_state(state, username=username)


@app.route("/scrape", methods=["POST"])
@login_required
def run_scraper():
    username = session.get("username")
    state = load_scrape_state(username=username)
    if state.get("running"):
        return jsonify({"ok": False, "message": "A pull is already in progress."}), 409

    # Create a unique pull ID
    pull_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_interests = load_interests(username=username)

    state = {
        "running": True,
        "message": "Starting...",
        "items_found": 0,
        "pull_id": pull_id,
    }
    save_scrape_state(state, username=username)

    thread = threading.Thread(target=_run_scraper_task, args=(pull_id, username, user_interests), daemon=True)
    thread.start()

    return jsonify({"ok": True, "message": "Pull started."})


@app.route("/scrape/status")
@login_required
def scrape_progress():
    username = session.get("username")
    state = load_scrape_state(username=username)
    return jsonify(state)


@app.route("/cleanup", methods=["POST"])
@login_required
def manual_cleanup():
    """Manually trigger cleanup of old scrape data (admin function)."""
    try:
        import db
        result = db.cleanup_old_scrapes(days_old=2)
        message = "Cleanup completed: deleted {} history entries and {} items older than {} days".format(
            result["history_deleted"], result["items_deleted"], result["days_old"]
        )
        print(message)
        flash(message, "success")
    except Exception as e:
        error_msg = "Cleanup failed: {}".format(e)
        print(error_msg)
        flash(error_msg, "error")

    return redirect(url_for("index"))


# --- Settings ---
@app.route("/settings")
@login_required
def settings():
    return render_template(
        "settings.html", 
        interests=load_interests(username=session.get("username")), 
        user=get_user_info(),
        schedule=load_schedule()
    )


@app.route("/settings/schedule", methods=["POST"])
@login_required
def update_schedule():
    enabled = request.form.get("nightly_scan") == "true"
    
    config = {"enabled": enabled}
    if save_schedule(config):
        status = "enabled" if enabled else "disabled"
        flash("Nightly scan {}.".format(status), "success")
    else:
        flash("Error saving schedule settings.", "error")
        
    return redirect(url_for("settings"))


@app.route("/settings/add", methods=["POST"])
@login_required
def add_interest():
    category = request.form.get("category")
    keywords_str = request.form.get("keywords")
    username = session.get("username")

    if category and keywords_str:
        keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
        interests = load_interests(username=username)
        interests[category] = keywords
        if save_interests(interests, username=username):
            flash("Added interest category: {}".format(category), "success")
        else:
            flash("Error saving interest.", "error")
    else:
        flash("Category and keywords are required.", "error")

    return redirect(url_for("settings"))


@app.route("/settings/delete", methods=["POST"])
@login_required
def delete_interest():
    category = request.form.get("category")
    username = session.get("username")
    if category:
        interests = load_interests(username=username)
        if category in interests:
            del interests[category]
            if save_interests(interests, username=username):
                flash("Deleted interest category: {}".format(category), "success")
            else:
                flash("Error saving changes.", "error")
        else:
            flash("Category not found.", "error")

    return redirect(url_for("settings"))


# --- History ---
# @app.route("/history") - Moved to index
# @login_required
# def history():
#     try:
#         scrape_history = db.load_history()
#     except Exception as e:
#         print(f"Error loading history from DB: {e}")
#         scrape_history = []
#         flash("Error loading history from database.", "error")
#     
#     return render_template(
#         "history.html", history=scrape_history, user=get_user_info()
#     )


@app.route("/pull/<pull_id>")
@login_required
def pull_detail(pull_id):
    """Show the data from a specific pull."""
    try:
        deals = db.load_pull_items(pull_id)
        
        # Find the history entry for this pull
        history = db.load_history(user_id=session.get("username"))
        entry = next((e for e in history if e.get("pull_id") == pull_id), None)
        pull_name = entry["timestamp"] if entry else pull_id
    except Exception as e:
        print("Error loading pull {}: {}".format(pull_id, e))
        deals = []
        pull_name = pull_id
        flash("Error loading pull data from database.", "error")

    categories = sorted(list(set(d.get("Interest Category", "Unknown") for d in deals)))

    return render_template(
        "pull_detail.html",
        deals=deals,
        pull_name=pull_name,
        pull_id=pull_id,
        total_items=len(deals),
        categories=categories,
        user=get_user_info(),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

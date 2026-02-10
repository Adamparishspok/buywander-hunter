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

import scraper
import db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# --- File paths (for things still in JSON) ---
INTERESTS_FILE = "interests.json"
USERS_FILE = "users.json"
SCRAPE_STATE_FILE = "scrape_state.json"


# --- Scrape state (file-based, survives restarts) ---
def load_scrape_state():
    """Load current scrape state from disk."""
    if os.path.exists(SCRAPE_STATE_FILE):
        try:
            with open(SCRAPE_STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"running": False, "message": "", "items_found": 0, "pull_id": None}


def save_scrape_state(state):
    """Persist scrape state to disk."""
    try:
        with open(SCRAPE_STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Error saving scrape state: {e}")


# On startup: if state says "running" but no thread is alive, mark it failed
_startup_state = load_scrape_state()
if _startup_state.get("running"):
    print("Previous scrape was interrupted. Marking as failed.")
    _startup_state["running"] = False
    _startup_state["message"] = "Interrupted by server restart"
    save_scrape_state(_startup_state)


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
            print(f"Error loading users: {e}")

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
        print(f"Error saving users: {e}")
        return False


def verify_user(username, password):
    users = load_users()
    if username in users:
        return hash_password(password) == users[username]["password"]
    return False


# --- Interest helpers (still JSON-based) ---
def load_interests():
    if os.path.exists(INTERESTS_FILE):
        try:
            with open(INTERESTS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading interests: {e}")
    return {}


def save_interests(interests):
    try:
        with open(INTERESTS_FILE, "w") as f:
            json.dump(interests, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving interests: {e}")
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
            flash(f'Welcome back, {session["display_name"]}!', "success")
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
        scrape_history = db.load_history()
    except Exception as e:
        print(f"Error loading history from DB: {e}")
        scrape_history = []
        flash("Error loading history from database.", "error")
    
    return render_template(
        "index.html", history=scrape_history, user=get_user_info()
    )


# --- Scraper background task ---
def _run_scraper_task(pull_id):
    """Background task that runs the scraper and saves to database."""
    try:
        state = load_scrape_state()
        state["message"] = "Fetching auctions from BuyWander..."
        save_scrape_state(state)
        print(f"Starting scraper for pull {pull_id}...")

        # Run the scraper - it returns a list of items
        items = scraper.monitor_deals()

        items_count = len(items)
        print(f"Scraper done. Found {items_count} items for pull {pull_id}.")

        # Save to database
        timestamp = datetime.now().strftime("%b %d, %Y - %I:%M %p")
        db.save_pull_history(pull_id, timestamp, "success", items_count)
        if items:
            db.save_pull_items(pull_id, items)

        state = load_scrape_state()
        state["message"] = f"Done! Found {items_count} products."
        state["items_found"] = items_count
        state["running"] = False
        save_scrape_state(state)
    except Exception as e:
        print(f"Error in scraper: {e}")
        import traceback
        traceback.print_exc()

        timestamp = datetime.now().strftime("%b %d, %Y - %I:%M %p")
        db.save_pull_history(pull_id, timestamp, "error", 0, str(e))

        state = load_scrape_state()
        state["message"] = f"Error: {e}"
        state["running"] = False
        save_scrape_state(state)


@app.route("/scrape", methods=["POST"])
@login_required
def run_scraper():
    state = load_scrape_state()
    if state.get("running"):
        return jsonify({"ok": False, "message": "A pull is already in progress."}), 409

    # Create a unique pull ID
    pull_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    state = {
        "running": True,
        "message": "Starting...",
        "items_found": 0,
        "pull_id": pull_id,
    }
    save_scrape_state(state)

    thread = threading.Thread(target=_run_scraper_task, args=(pull_id,), daemon=True)
    thread.start()

    return jsonify({"ok": True, "message": "Pull started."})


@app.route("/scrape/status")
@login_required
def scrape_progress():
    state = load_scrape_state()
    return jsonify(state)


# --- Settings ---
@app.route("/settings")
@login_required
def settings():
    return render_template(
        "settings.html", interests=load_interests(), user=get_user_info()
    )


@app.route("/settings/add", methods=["POST"])
@login_required
def add_interest():
    category = request.form.get("category")
    keywords_str = request.form.get("keywords")

    if category and keywords_str:
        keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
        interests = load_interests()
        interests[category] = keywords
        if save_interests(interests):
            flash(f"Added interest category: {category}", "success")
        else:
            flash("Error saving interest.", "error")
    else:
        flash("Category and keywords are required.", "error")

    return redirect(url_for("settings"))


@app.route("/settings/delete", methods=["POST"])
@login_required
def delete_interest():
    category = request.form.get("category")
    if category:
        interests = load_interests()
        if category in interests:
            del interests[category]
            if save_interests(interests):
                flash(f"Deleted interest category: {category}", "success")
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
        history = db.load_history()
        entry = next((e for e in history if e.get("pull_id") == pull_id), None)
        pull_name = entry["timestamp"] if entry else pull_id
    except Exception as e:
        print(f"Error loading pull {pull_id}: {e}")
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

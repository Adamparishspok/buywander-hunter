import os
import time
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import scraper
from datetime import datetime
import hashlib

import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

CSV_FILE = 'buywander_interests.csv'
INTERESTS_FILE = 'interests.json'
HISTORY_FILE = 'scrape_history.json'
USERS_FILE = 'users.json'

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
    
    # Create default users if file doesn't exist
    default_users = {
        "Adam": {
            "password": hash_password("adam123"),
            "display_name": "Adam",
            "initials": "AP"
        },
        "Alex": {
            "password": hash_password("alex123"),
            "display_name": "Alex",
            "initials": "AP"
        }
    }
    save_users(default_users)
    return default_users

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def verify_user(username, password):
    """Verify username and password"""
    users = load_users()
    if username in users:
        hashed_input = hash_password(password)
        return hashed_input == users[username]['password']
    return False

def load_interests():
    if os.path.exists(INTERESTS_FILE):
        try:
            with open(INTERESTS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading interests: {e}")
    return {}

def save_interests(interests):
    try:
        with open(INTERESTS_FILE, 'w') as f:
            json.dump(interests, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving interests: {e}")
        return False

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False

def add_history_entry(status, items_found, error_msg=None):
    history = load_history()
    entry = {
        'timestamp': datetime.now().isoformat(),
        'status': status,
        'items_found': items_found,
        'error': error_msg
    }
    history.insert(0, entry)  # Add to beginning
    # Keep only last 50 entries
    history = history[:50]
    save_history(history)

def load_deals():
    if not os.path.exists(CSV_FILE):
        return [], "Never"
    
    try:
        df = pd.read_csv(CSV_FILE)
        # Convert to list of dicts
        deals = df.to_dict('records')
        
        # Get last modified time
        mod_time = os.path.getmtime(CSV_FILE)
        last_updated = time.ctime(mod_time)
        
        return deals, last_updated
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return [], "Error reading data"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_user(username, password):
            session['logged_in'] = True
            session['username'] = username
            
            # Get user info for display
            users = load_users()
            session['display_name'] = users[username]['display_name']
            session['initials'] = users[username]['initials']
            
            flash(f'Welcome back, {session["display_name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('display_name', None)
    session.pop('initials', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    deals, last_updated = load_deals()
    # Get unique categories for filtering
    categories = sorted(list(set(d.get('Interest Category', 'Unknown') for d in deals)))
    
    # Get user info from session
    user_info = {
        'display_name': session.get('display_name', 'User'),
        'initials': session.get('initials', 'U')
    }
    
    return render_template('index.html', deals=deals, last_updated=last_updated, total_items=len(deals), categories=categories, user=user_info)

@app.route('/scrape', methods=['POST'])
@login_required
def run_scraper():
    try:
        # Run the scraper
        scraper.monitor_deals()
        
        # Count items found
        deals, _ = load_deals()
        items_count = len(deals)
        
        # Log success
        add_history_entry('success', items_count)
        flash("Scraping complete! Data updated.", "success")
    except Exception as e:
        # Log failure
        add_history_entry('error', 0, str(e))
        flash(f"Error running scraper: {e}", "error")
    
    return redirect(url_for('index'))

@app.route('/settings')
@login_required
def settings():
    interests = load_interests()
    
    # Get user info from session
    user_info = {
        'display_name': session.get('display_name', 'User'),
        'initials': session.get('initials', 'U')
    }
    
    return render_template('settings.html', interests=interests, user=user_info)

@app.route('/settings/add', methods=['POST'])
@login_required
def add_interest():
    category = request.form.get('category')
    keywords_str = request.form.get('keywords')
    
    if category and keywords_str:
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
        interests = load_interests()
        interests[category] = keywords
        if save_interests(interests):
            flash(f"Added interest category: {category}", "success")
        else:
            flash("Error saving interest.", "error")
    else:
        flash("Category and keywords are required.", "error")
        
    return redirect(url_for('settings'))

@app.route('/settings/delete', methods=['POST'])
@login_required
def delete_interest():
    category = request.form.get('category')
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
    
    return redirect(url_for('settings'))

@app.route('/history')
@login_required
def history():
    scrape_history = load_history()
    
    # Get user info from session
    user_info = {
        'display_name': session.get('display_name', 'User'),
        'initials': session.get('initials', 'U')
    }
    
    return render_template('history.html', history=scrape_history, user=user_info)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

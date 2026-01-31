import os
import time
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import scraper

import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# Simple auth config
ADMIN_USERNAME = os.environ.get("APP_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("APP_PASSWORD", "admin")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

CSV_FILE = 'buywander_interests.csv'
INTERESTS_FILE = 'interests.json'

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
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Successfully logged in.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    deals, last_updated = load_deals()
    return render_template('index.html', deals=deals, last_updated=last_updated, total_items=len(deals))

@app.route('/scrape', methods=['POST'])
@login_required
def run_scraper():
    try:
        # Run the scraper
        scraper.monitor_deals()
        flash("Scraping complete! Data updated.", "success")
    except Exception as e:
        flash(f"Error running scraper: {e}", "error")
    
    return redirect(url_for('index'))

@app.route('/settings')
@login_required
def settings():
    interests = load_interests()
    return render_template('settings.html', interests=interests)

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

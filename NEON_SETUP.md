# Neon Database Setup Complete

## What Changed

Your BuyWander scraper now uses **Neon Postgres** to store pull history and product data. This ensures data persists across Railway deploys (Railway's filesystem is ephemeral).

### Files Modified

- `web_app.py` - Now uses database instead of JSON/CSV files for pulls
- `scraper.py` - Returns items list instead of writing CSV, optimized for speed
- `requirements.txt` - Added `psycopg2-binary`
- `db.py` - **NEW** database helper module
- `templates/index.html` - Fixed template bug
- `templates/history.html` - History entries are now clickable
- `templates/pull_detail.html` - **NEW** page to view individual pull data

### Database Schema

- `scrape_history` table - Stores pull metadata (pull_id, timestamp, status, items_found)
- `pull_items` table - Stores product details for each pull

## Neon Project Details

**Project Name:** buywander  
**Project ID:** gentle-base-21176446  
**Database:** neondb

**Connection String:**

```
postgresql://neondb_owner:npg_QltRB7TGCb0r@ep-nameless-mouse-af40upqp-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require
```

## Local Testing

The app is currently running at http://127.0.0.1:5000 with the DATABASE_URL environment variable set.

You can also use `./run_web.sh` which has the DATABASE_URL pre-configured.

## Railway Deployment

To deploy to Railway with Neon:

1. **Add DATABASE_URL to Railway Environment Variables:**

   ```
   DATABASE_URL=postgresql://neondb_owner:npg_QltRB7TGCb0r@ep-nameless-mouse-af40upqp-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require
   ```

2. **Deploy as usual** - Railway will use the `Procfile` which runs `gunicorn web_app:app`

3. **Optional: Set other env vars:**
   - `SECRET_KEY` - Flask session secret (generate a random string)
   - `APP_PASSWORD` - If you still use the old app.py Streamlit version

## How It Works Now

1. **Pull Products** button triggers an AJAX request
2. Scraper runs in a background thread (20-30 seconds)
3. Results are saved to Neon database
4. Page auto-reloads showing the new data
5. **History entries are clickable** - click any pull to see its specific data
6. Each pull gets a unique ID (timestamp-based) and its own data

## Performance

- Fetches 10 pages (1000 items) from BuyWander
- 100 items per page for efficiency
- Completes in ~20-25 seconds
- Found 172-180 products in test runs

## What's Still in JSON Files

These will be lost on Railway deploys - consider migrating later:

- `users.json` - User accounts
- `interests.json` - Interest categories and keywords
- `scrape_state.json` - Transient "is running" state (OK to be ephemeral)

## Testing

✅ Database connection works
✅ Scraper completes and finds products
✅ History is saved to database
✅ Pull items are saved to database
✅ Dashboard loads latest pull data
✅ History page shows all pulls
✅ Clicking history entry shows pull details
✅ Loading overlay appears during pull
✅ Concurrent pulls are blocked

# Railway Deployment Guide

## ✅ Code Pushed!

Your code has been pushed to GitHub: `Adamparishspok/buywander-hunter`

Railway should automatically detect the push and start deploying.

## 🔧 Required: Set Environment Variable

**You MUST add the DATABASE_URL to Railway for the app to work:**

1. Go to your Railway project dashboard
2. Click on your service (web app)
3. Go to **Variables** tab
4. Click **+ New Variable**
5. Add:

```
DATABASE_URL=postgresql://neondb_owner:<YOUR_PASSWORD>@ep-nameless-mouse-af40upqp-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require
```

> Get the actual password from your `.env` file or the Neon console.

6. Click **Save** - Railway will automatically redeploy

## Optional Environment Variables

```bash
# Flask session secret (generate a strong random string)
SECRET_KEY=your-random-secret-key-here

# If you want to change default passwords later
# (users.json will reset on each deploy since it's in filesystem)
```

## What Happens on Deploy

1. Railway detects the push to `main`
2. Installs dependencies from `requirements.txt` (includes `psycopg2-binary`)
3. Runs `gunicorn web_app:app` (from Procfile)
4. Connects to your Neon database using `DATABASE_URL`
5. App is live! 🎉

## After Deploy

- **Login:** Adam / adam123 (or Alex / alex123)
- Click **"Pull Products"** to start scraping
- View results on Dashboard
- Check **Scrape History** for all past pulls
- Click any history entry to see its specific data

## ⚠️ Important Notes

### Data That Persists (in Neon DB)
- ✅ Pull history
- ✅ Product data from each pull
- ✅ Survives Railway deploys/restarts

### Data That Resets on Deploy
- ❌ `users.json` - User accounts reset to defaults
- ❌ `interests.json` - Interest categories reset to defaults
- ❌ `scrape_state.json` - Transient state (OK to reset)

### Recommended: Migrate users/interests to Neon

Consider adding these tables in a future update:
- `users` table for persistent user accounts
- `interests` table for persistent interest categories

For now, you can:
- Set them via environment variables
- Add a seed script that runs on startup
- Or just reconfigure them after each deploy

## Neon Project Info

**Project:** buywander (gentle-base-21176446)  
**Database:** neondb  
**Region:** AWS US West 2  
**Console:** https://console.neon.tech/app/projects/gentle-base-21176446

## Testing Deployment

Once Railway finishes deploying (usually 2-3 minutes):

1. Open your Railway app URL
2. Login with Adam / adam123
3. Click "Pull Products"
4. Wait ~20-30 seconds
5. Dashboard shows ~170-180 products
6. Go to Scrape History - you'll see the pull
7. Click it to view that pull's data

## Troubleshooting

If the app crashes on Railway:

1. Check Railway logs for errors
2. Verify `DATABASE_URL` is set correctly
3. Make sure it includes `?sslmode=require` at the end
4. Check that psycopg2-binary installed (should be in requirements.txt)

# Railway Deployment Guide

We have configured the application to run as two services on Railway:
1.  **Auth Server** (Node.js) - Handles authentication.
2.  **Main App** (Python/FastAPI + Vue) - Runs the backend and serves the frontend.

## Prerequisites

1.  **Railway Account** connected to your GitHub repo.
2.  **Railway CLI** installed and logged in (`railway login`).

## Step 1: Create Project & Database

1.  Go to [Railway Dashboard](https://railway.app/dashboard).
2.  Click **New Project** -> **Provision PostgreSQL**.
3.  This creates a project with a database.

## Step 2: Deploy Auth Server

1.  In the project view, click **New** -> **GitHub Repo**.
2.  Select your repo (`buywander`).
3.  Click **Variables** and add:
    *   `DATABASE_URL`: (Reference the Postgres variable, usually `${{Postgres.DATABASE_URL}}`)
    *   `BETTER_AUTH_SECRET`: Generate a random string (e.g. `openssl rand -hex 32`).
    *   `BETTER_AUTH_URL`: `https://auth-server-production-acc6.up.railway.app`
    *   `PORT`: `3001`
4.  Click **Settings** -> **General** -> **Root Directory**: Set to `/auth-server`.
5.  Click **Settings** -> **Networking** -> **Generate Domain**.
6.  Copy this domain (e.g. `https://auth-production.up.railway.app`) and update the `BETTER_AUTH_URL` variable from step 3.
7.  The service should redeploy and be healthy.

## Step 3: Deploy Main App

1.  Click **New** -> **GitHub Repo** (Select the same repo again).
2.  Click **Variables** and add:
    *   `DATABASE_URL`: `${{Postgres.DATABASE_URL}}`
    *   `SECRET_KEY`: Generate a random string.
    *   `BETTER_AUTH_URL`: `https://auth-server-production-acc6.up.railway.app`
    *   `PORT`: `8000`
3.  Click **Settings** -> **General** -> **Root Directory**: Leave empty (`/`).
4.  Railway will detect the `Dockerfile` in the root and build it.
5.  Click **Settings** -> **Networking** -> **Generate Domain**.
6.  This is your main application URL: `https://main-app-production-fea8.up.railway.app`

## Step 4: Final Configuration

1.  **CORS**: Ensure your Auth Server allows requests from your Main App.
    *   In **Auth Server** variables, you might need to check `better-auth` trusted origins.
    *   However, since we are proxying auth requests through the Main App backend, the requests come from the Main App's backend IP (server-to-server) or appear as same-origin to the browser.
    *   Our setup proxies `/api/auth` from Main App -> Auth Server.
    *   So the browser only talks to Main App.
    *   This simplifies CORS significantly!

## Troubleshooting

*   **Build Fails**: Check the logs. Ensure `pnpm-lock.yaml` is present.
*   **Auth Errors**: Check `BETTER_AUTH_URL` in Main App matches Auth Server URL.
*   **Database**: Ensure both services use the same `DATABASE_URL`.

## Local Development vs Production

*   **Local**: Frontend talks to Vite (:5173) -> Proxy to Backend (:8000) -> Proxy to Auth (:3001).
*   **Production**: Frontend talks to Backend (:8000) -> Proxy to Auth (:3001).

No changes needed in frontend code!

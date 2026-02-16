# Railway Deployment Guide

Since we've upgraded to a monorepo structure with a dedicated Auth Server, deployment requires two services on Railway.

## Prerequisites

1.  **Railway Account** connected to your GitHub repo.
2.  **PostgreSQL Database** (Neon or Railway Postgres).

## Service 1: Auth Server (Node.js)

This service handles authentication (signup, login, sessions).

1.  **Create New Service** -> **GitHub Repo** -> Select your repo.
2.  **Configure Service**:
    *   **Root Directory**: `auth-server`
    *   **Build Command**: `pnpm install && pnpm run build`
    *   **Start Command**: `pnpm start`
    *   **Watch Paths**: `auth-server/**` (optional)
3.  **Environment Variables**:
    *   `DATABASE_URL`: Connection string to your Postgres DB (same as backend).
    *   `BETTER_AUTH_SECRET`: A random string (generate one).
    *   `BETTER_AUTH_URL`: The public URL of *this* service (e.g., `https://auth-production.up.railway.app`).
    *   `PORT`: `3001` (Railway usually overrides this, but good to set).

## Service 2: Main App (Backend + Frontend)

This service runs the FastAPI backend and serves the Vue frontend.

1.  **Create New Service** -> **GitHub Repo** -> Select your repo.
2.  **Configure Service**:
    *   **Root Directory**: `/` (leave empty)
    *   **Docker**: Railway should automatically detect the `Dockerfile`.
3.  **Environment Variables**:
    *   `DATABASE_URL`: Same Postgres connection string.
    *   `SECRET_KEY`: A random string for internal encryption.
    *   `BETTER_AUTH_URL`: The public URL of the **Auth Server** (from step 1).
    *   `PORT`: `8000`

## Networking

1.  **Auth Server**: Needs a public domain (e.g., `auth-production.up.railway.app`).
2.  **Main App**: Needs a public domain (e.g., `buywander-production.up.railway.app`).

## Important Notes

*   **CORS**: Ensure your `BETTER_AUTH_URL` environment variable in the Main App matches the Auth Server's domain exactly.
*   **Database**: Both services MUST connect to the same database. Better Auth manages the `user`, `session`, etc. tables, while FastAPI reads from them.
*   **Migrations**: The Main App (FastAPI) handles migrations via Alembic. You might need to run `alembic upgrade head` in the Main App's shell or as a startup command if not automated.

## Troubleshooting

*   **Frontend 404s**: If the frontend doesn't load, ensure the Docker build completed successfully and `static/index.html` exists in the container.
*   **Auth Errors**: Check that `BETTER_AUTH_URL` is correct in both services and that they share the same `DATABASE_URL`.

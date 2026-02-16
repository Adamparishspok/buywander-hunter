# BuyWander Deal Hunter - Better Auth Edition

A modern web application for tracking and monitoring deals from BuyWander auctions, built with Better Auth, FastAPI, and Vue 3.

## 🚀 Tech Stack

### Authentication
- **Better Auth** - Modern, type-safe authentication framework
- **Email/Password** - Secure credential-based auth
- **JWT Tokens** - Stateless authentication with automatic refresh

### Backend (Chad Python Energy)
- **FastAPI** - Blazing fast async Python web framework
- **SQLModel** - Pydantic + SQLAlchemy fusion for type-safe ORM
- **PostgreSQL (Neon)** - Async database with asyncpg driver
- **Alembic** - Database migrations
- **Ruff** - Lightning-fast Python linter
- **Uvicorn** - ASGI server for production performance

### Frontend (Vue 3 Chad Mode)
- **Vue 3** - Composition API with `<script setup>`
- **TypeScript** - Strict mode for type safety
- **Vite** - Next-gen frontend tooling
- **Pinia** - Official Vue state management
- **Vue Router** - Client-side routing
- **Axios** - HTTP client with interceptors
- **Tailwind CSS** - Utility-first styling
- **shadcn-vue** - Beautiful, accessible components
- **Lucide Vue** - Icon library

## 📦 Prerequisites

- Python 3.11+
- Node.js 22.1.0+ (with pnpm)
- PostgreSQL (Neon)

## 🛠️ Setup

### Quick Start (All Services)

Run all three services with one command:

```bash
./start-dev.sh
```

This starts:
- Auth Server (Better Auth) on `http://localhost:3001`
- Backend API (FastAPI) on `http://localhost:8000`
- Frontend (Vue 3) on `http://localhost:5173`

Then visit `http://localhost:5173` in your browser.

### Manual Setup

#### 1. Auth Server

```bash
cd auth-server
pnpm install
# Copy .env.example to .env and configure DATABASE_URL
pnpm run dev
```

#### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
# Configure .env with DATABASE_URL and BETTER_AUTH_URL
uvicorn main:app --reload --port 8000
```

#### 3. Frontend Setup

```bash
cd frontend
pnpm install
pnpm run dev
```

## 🏗️ Architecture

```
┌─────────────┐
│   Vue 3     │
│  Frontend   │──────┐
│  :5173      │      │
└─────────────┘      │
                     │ Auth requests
                     ↓
              ┌──────────────┐
              │ Better Auth  │
              │ Auth Server  │────────┐
              │   :3001      │        │
              └──────────────┘        │
                     ↑                │
                     │ Token verify   │ Read/Write
┌─────────────┐     │                │
│   FastAPI   │─────┘                ↓
│   Backend   │              ┌──────────────┐
│   :8000     │──────────────│    Neon      │
└─────────────┘ Business     │  PostgreSQL  │
                logic         └──────────────┘
```

## 📋 Features

- ✅ **Better Auth Integration** - Industry-standard authentication
- ✅ **Email/Password Auth** - Secure credential management
- ✅ **JWT Tokens** - Automatic token refresh
- ✅ **Product Scraping** - Automated BuyWander auction monitoring
- ✅ **Scrape History** - Track all past scraping runs
- ✅ **Smart Filtering** - Configure interests and keywords
- ✅ **Scheduled Scans** - Automatic nightly scraping
- ✅ **Data Cleanup** - Automatic removal of old data
- ✅ **Pull Details** - View deals with list/grid modes
- ✅ **TypeScript** - End-to-end type safety
- ✅ **Modern UI** - Dark theme with Tailwind + shadcn-vue

## 🔌 API Endpoints

### Authentication (Better Auth Server - :3001)
- `POST /api/auth/sign-up/email` - Create account
- `POST /api/auth/sign-in/email` - Login
- `POST /api/auth/sign-out` - Logout
- `GET /api/auth/get-session` - Get session

### API (FastAPI Backend - :8000)
- `GET /api/auth/me` - Get current user
- `POST /api/scrape` - Start scrape job
- `GET /api/scrape/status` - Get job status
- `GET /api/history` - Get scrape history
- `GET /api/settings` - Get user settings
- `POST /api/settings/schedule` - Update schedule
- `POST /api/settings/interests` - Add interest category
- `DELETE /api/settings/interests/:category` - Delete category
- `GET /api/pull/:pullId` - Get pull details
- `POST /api/cleanup` - Manual data cleanup

## 🔐 Environment Variables

### Auth Server (`auth-server/.env`)
```env
DATABASE_URL=postgresql://...
PORT=3001
NODE_ENV=development
BETTER_AUTH_SECRET=your-random-secret
BETTER_AUTH_URL=http://localhost:3001
```

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=your-secret-key
BETTER_AUTH_URL=http://localhost:3001
```

## 🐳 Docker Deployment

Coming soon - multi-stage build with all three services.

## 📂 Project Structure

```
buywander/
├── auth-server/         # Better Auth server (Node.js)
│   ├── src/
│   │   ├── auth.ts     # Better Auth config
│   │   └── index.ts    # Express server
│   └── package.json
├── backend/             # FastAPI backend (Python)
│   ├── main.py         # Main application
│   ├── models.py       # SQLModel models
│   ├── database.py     # Async DB connection
│   ├── auth_utils.py   # Token verification
│   └── requirements.txt
├── frontend/            # Vue 3 + TypeScript
│   ├── src/
│   │   ├── api/        # Axios client
│   │   ├── stores/     # Pinia stores (uses Better Auth)
│   │   ├── router/     # Vue Router
│   │   ├── views/      # Page components
│   │   ├── lib/        # Better Auth client
│   │   └── components/ # UI components + shadcn-vue
│   └── package.json
└── start-dev.sh        # Start all services
```

## 🔐 Security Features

- **Better Auth** - Production-ready authentication framework
- **JWT Tokens** - Secure, stateless authentication
- **httpOnly Cookies** - Secure token storage
- **CORS Protection** - Configured for frontend origins
- **Token Verification** - FastAPI verifies all requests
- **Auth Guards** - Protected routes in Vue Router

## 🧪 Development

### Auth Server
```bash
cd auth-server
pnpm run dev  # Watch mode with tsx
```

### Backend Linting
```bash
cd backend
ruff check .
ruff format .
```

### Frontend Type Checking
```bash
cd frontend
pnpm run type-check  # or npx vue-tsc --noEmit
```

## 🌟 Why Better Auth?

- **Type-Safe** - Full TypeScript support
- **Modern** - Built for 2026 best practices
- **Feature-Rich** - Email verification, OAuth, 2FA ready
- **Active Development** - Regular updates
- **Database Agnostic** - Works with any SQL database
- **Same Database** - Auth and app data in one place (Neon)

## 📝 License

MIT

---

Built with Better Auth + FastAPI + Vue 3 TypeScript 🚀

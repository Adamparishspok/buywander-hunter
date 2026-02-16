# Quick Start Guide - Gigachad Stack Edition

## What Is This?

A modern deal tracking app built with:
- **Backend**: FastAPI (async Python) with JWT auth
- **Frontend**: Vue 3 + TypeScript + Tailwind + shadcn-vue
- **Database**: PostgreSQL (Neon) with SQLModel ORM

## One-Command Start

```bash
./start-dev.sh
```

That's it! Visit `http://localhost:5173`

**What it does:**
- Starts FastAPI backend on port 8000
- Starts Vue 3 frontend on port 5173
- Proxy configured automatically

## First Time Setup

### 1. Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Frontend Dependencies

```bash
cd frontend
pnpm install
```

### 3. Environment Variables

Create `backend/.env`:
```env
DATABASE_URL=your_postgresql_url
SECRET_KEY=change-me-in-production
```

### 4. Database Setup

```bash
cd backend
alembic upgrade head
```

## Manual Start (Alternative)

If you prefer running each server separately:

**Terminal 1 (Backend):**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
pnpm run dev
```

## Key URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Main app |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Interactive Swagger UI |
| Redoc | http://localhost:8000/redoc | Alternative API docs |

## First Steps

1. **Sign Up**: Create account at `/signup`
2. **Login**: Use your credentials
3. **Configure**: Go to Settings → Add interests
4. **Scrape**: Click "Pull Products" on dashboard
5. **View**: Check scrape history and results

## Tech Stack Highlights

### Backend (Fast as F*)
- **FastAPI** - Async Python web framework
- **SQLModel** - Type-safe ORM (Pydantic + SQLAlchemy)
- **JWT Auth** - Secure token-based authentication
- **asyncpg** - Async PostgreSQL driver
- **Uvicorn** - Lightning-fast ASGI server

### Frontend (Type-Safe & Beautiful)
- **Vue 3** - Composition API with `<script setup>`
- **TypeScript** - Strict mode for bulletproof code
- **Vite** - Instant HMR and fast builds
- **Pinia** - Vue's official state management
- **Tailwind CSS** - Utility-first styling
- **shadcn-vue** - Premium component library

## Common Commands

### Development
```bash
# Run both servers
./start-dev.sh

# Backend only
cd backend && uvicorn main:app --reload

# Frontend only
cd frontend && pnpm run dev
```

### Database
```bash
# Create migration
cd backend && alembic revision --autogenerate -m "description"

# Apply migrations
cd backend && alembic upgrade head

# Rollback
cd backend && alembic downgrade -1
```

### Build
```bash
# Frontend production build
cd frontend && pnpm run build

# Docker build
docker build -t buywander .
```

### Code Quality
```bash
# Backend linting
cd backend && ruff check .

# Backend formatting
cd backend && ruff format .

# Frontend type check
cd frontend && pnpm exec vue-tsc --noEmit
```

## Project Structure

```
buywander/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # SQLModel models
│   ├── database.py          # Async DB connection
│   ├── auth_utils.py        # JWT auth
│   ├── alembic/             # Migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios client
│   │   ├── stores/         # Pinia stores
│   │   ├── router/         # Vue Router
│   │   ├── views/          # Pages
│   │   ├── components/     # UI components + shadcn-vue
│   │   └── types.ts        # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── Dockerfile              # Production build
└── start-dev.sh           # Dev startup script
```

## API Examples

### Authentication
```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'
```

### Scraping (requires auth token)
```bash
# Start scrape
curl -X POST http://localhost:8000/api/scrape \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check status
curl http://localhost:8000/api/scrape/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get history
curl http://localhost:8000/api/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Features

✅ JWT authentication (access + refresh tokens)  
✅ Async database operations  
✅ Auto-generated API docs  
✅ Type-safe frontend (TypeScript)  
✅ Beautiful UI (Tailwind + shadcn-vue)  
✅ Product scraping from BuyWander  
✅ Scrape history tracking  
✅ Interest categories  
✅ Scheduled nightly scans  
✅ Data cleanup  
✅ List/grid view modes  

## Troubleshooting

**Backend won't start?**
- Check Python version (3.11+)
- Run `pip install -r requirements.txt`
- Verify `.env` file exists

**Frontend won't start?**
- Check Node version (22.1.0+)
- Run `pnpm install`
- Clear `node_modules` and reinstall

**Database errors?**
- Check `DATABASE_URL` in `.env`
- For async: should be `postgresql+asyncpg://...`
- Run migrations: `alembic upgrade head`

**Auth not working?**
- Clear browser localStorage
- Check backend is on port 8000
- Verify SECRET_KEY in `.env`

## Production Deployment

### Docker
```bash
# Build
docker build -t buywander .

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  -e SECRET_KEY=your_secret \
  buywander
```

### Railway / Render
1. Push to GitHub
2. Connect repo to Railway/Render
3. Set environment variables
4. Deploy!

## What's Next?

1. Explore API docs at `/docs`
2. Add your interests in Settings
3. Run your first scrape
4. Check out the shadcn-vue components
5. Customize the UI with Tailwind

---

Built with the 2026 Gigachad Stack 🚀

Need help? Check `README.md` for full documentation.

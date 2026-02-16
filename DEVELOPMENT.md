# Development Guide

Complete development workflow for BuyWander Deal Hunter.

## Quick Commands

All commands from root directory:

```bash
# Start all services
./start-dev.sh

# Or use npm
pnpm run dev

# Lint everything
pnpm run lint

# Format everything
pnpm run format

# Type check everything
pnpm run type-check

# Install all dependencies
pnpm run install:all
```

## Service-Specific Commands

### Auth Server (Port 3001)

```bash
cd auth-server

# Development
pnpm run dev              # Start with hot reload

# Code Quality
pnpm run lint             # ESLint check
pnpm run lint:fix         # ESLint auto-fix
pnpm run format           # Prettier format
pnpm run format:check     # Check formatting
tsc --noEmit            # Type check

# Build
pnpm run build           # Compile TypeScript
pnpm start              # Run compiled code
```

### Backend (Port 8000)

```bash
cd backend

# Development
uvicorn main:app --reload --port 8000  # Start server
# Or use make
make dev

# Code Quality
make lint               # Ruff check
make lint-fix          # Ruff auto-fix
make format            # Ruff format
make format-check      # Check formatting

# Database
alembic upgrade head   # Run migrations
alembic revision --autogenerate -m "message"  # Create migration

# Testing
make test              # Run pytest

# Cleanup
make clean            # Remove __pycache__
```

### Frontend (Port 5173)

```bash
cd frontend

# Development
pnpm run dev            # Start Vite dev server

# Code Quality
pnpm run lint           # ESLint check
pnpm run lint:fix       # ESLint auto-fix
pnpm run format         # Prettier format
pnpm run format:check   # Check formatting
pnpm run type-check     # TypeScript check

# Build
pnpm run build         # Production build
ppnpm run preview       # Preview production build
```

## IDE Setup

### VS Code (Recommended)

Install recommended extensions:
1. Ruff (Python linting/formatting)
2. ESLint (JS/TS linting)
3. Prettier (code formatting)
4. Vue - Official (Volar)
5. Tailwind CSS IntelliSense

Settings in `.vscode/settings.json` enable:
- Format on save
- Auto-fix on save
- Organize imports

### Cursor

Same extensions work in Cursor. Format on save is configured automatically.

## Git Workflow

### Pre-commit Hooks

Install once:
```bash
pip3 install pre-commit
pre-commit install
```

What it does:
- Runs Ruff on Python files before commit
- Runs Prettier on TS/Vue files before commit
- Checks trailing whitespace
- Validates YAML/JSON
- Prevents large files

### Manual Pre-commit Check

```bash
pre-commit run --all-files
```

### Commit Message Convention

Follow Conventional Commits:
```
<type>: <description>

Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore
```

Examples:
```bash
git commit -m "feat: add oauth provider support"
git commit -m "fix: resolve token refresh issue"
git commit -m "docs: update api documentation"
```

## Testing Workflow

### Backend Tests
```bash
cd backend
pytest                     # Run all tests
pytest tests/test_auth.py  # Run specific test
pytest -v                  # Verbose output
pytest --cov              # Coverage report
```

### Frontend Tests (when added)
```bash
cd frontend
pnpm run test              # Run tests
pnpm run test:coverage     # Coverage report
```

## Common Tasks

### Add New Route

**Backend:**
1. Add route function in `backend/main.py`
2. Format: `make format`
3. Lint: `make lint-fix`
4. Test manually or add pytest

**Frontend:**
1. Create view in `frontend/src/views/`
2. Add route in `frontend/src/router/index.ts`
3. Format: `pnpm run format`
4. Lint: `pnpm run lint:fix`

### Add New Model

**Backend:**
1. Add model to `backend/models.py`
2. Create migration: `alembic revision --autogenerate -m "add model"`
3. Review migration file
4. Apply: `alembic upgrade head`
5. Format: `make format`

### Update Dependencies

**Auth Server:**
```bash
cd auth-server
pnpm install package-name
pnpm install --save-dev dev-package-name
```

**Backend:**
```bash
cd backend
# Add to requirements.txt manually
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
pnpm install package-name
pnpm install --save-dev dev-package-name
```

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| Auth Server | 3001 | http://localhost:3001 |
| Backend API | 8000 | http://localhost:8000 |
| Frontend | 5173 | http://localhost:5173 |
| API Docs | 8000 | http://localhost:8000/docs |

## Environment Variables

### Required in each service:

**auth-server/.env:**
```env
DATABASE_URL=postgresql://...
PORT=3001
BETTER_AUTH_SECRET=random-secret
```

**backend/.env:**
```env
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=random-secret
BETTER_AUTH_URL=http://localhost:3001
```

## Debugging

### Backend
- Check logs in terminal
- Use `print()` or Python debugger
- FastAPI logs all requests
- API docs at `/docs` for testing

### Frontend
- Use Vue DevTools browser extension
- Check browser console
- Network tab for API calls
- Vue Router logs route changes

### Auth Server
- Check server logs
- Test endpoints with curl/Postman
- Verify database connection

## Performance Tips

### Backend
- Use async/await for all I/O operations
- Connection pooling configured in `database.py`
- Background jobs use APScheduler

### Frontend
- Lazy load routes with `() => import()`
- Use `v-memo` for expensive computed properties
- Vite optimizes bundle automatically

## Troubleshooting

### Linting fails
```bash
# Auto-fix most issues
pnpm run lint:fix           # Frontend/Auth
cd backend && make lint-fix # Backend
```

### Formatting inconsistent
```bash
# Format all projects
pnpm run format
```

### Type errors
```bash
# Check types
pnpm run type-check

# Common fixes:
# - Add missing type annotations
# - Update TypeScript/Vue types
# - Check tsconfig.json settings
```

### Pre-commit fails
```bash
# Run manually to see errors
pre-commit run --all-files

# Update hooks
pre-commit autoupdate

# Skip if needed (not recommended)
git commit --no-verify
```

## CI/CD

Add to GitHub Actions:

```yaml
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      
      - name: Install dependencies
        run: pnpm run install:all
      
      - name: Lint
        run: pnpm run lint
      
      - name: Format check
        run: pnpm run format:check
      
      - name: Type check
        run: pnpm run type-check
```

## Summary

Your development environment is now fully configured with:

✅ Consistent code formatting across all services  
✅ Automatic linting on save  
✅ Type checking for TypeScript  
✅ Pre-commit hooks  
✅ VS Code integration  
✅ CI/CD ready scripts  

Happy coding! 🚀

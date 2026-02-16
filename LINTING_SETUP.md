# Linting & Formatting Setup

Complete linting and formatting configuration for your Gigachad Stack.

## Overview

Your project now has consistent linting and formatting across all three services:

| Service | Linter | Formatter | Type Checker |
|---------|--------|-----------|--------------|
| **Auth Server** | ESLint | Prettier | TypeScript |
| **Backend** | Ruff | Ruff | Python (Pydantic) |
| **Frontend** | ESLint | Prettier | TypeScript |

## Quick Commands

### Run Everything (from root)

```bash
# Lint all projects
pnpm run lint

# Format all projects
pnpm run format

# Check formatting without modifying
pnpm run format:check

# Type check TypeScript projects
pnpm run type-check
```

### Individual Services

**Auth Server:**
```bash
cd auth-server
pnpm run lint          # ESLint
pnpm run lint:fix      # ESLint with auto-fix
pnpm run format        # Prettier format
pnpm run format:check  # Check formatting
```

**Backend:**
```bash
cd backend
make lint             # Ruff check
make lint-fix         # Ruff check with auto-fix
make format           # Ruff format
make format-check     # Check formatting
```

**Frontend:**
```bash
cd frontend
pnpm run lint          # ESLint
pnpm run lint:fix      # ESLint with auto-fix
pnpm run format        # Prettier format
pnpm run format:check  # Check formatting
pnpm run type-check    # TypeScript type checking
```

## Configuration Files

### Root Level
- `.prettierrc` - Prettier configuration (shared)
- `.prettierignore` - Files to ignore
- `.editorconfig` - Editor settings
- `.pre-commit-config.yaml` - Pre-commit hooks
- `package.json` - Root scripts for all services

### Auth Server
- `eslint.config.mjs` - ESLint for TypeScript
- `tsconfig.json` - TypeScript compiler options

### Backend
- `pyproject.toml` - Ruff configuration
- `.ruff.toml` - Additional Ruff settings
- `Makefile` - Development shortcuts

### Frontend
- `eslint.config.js` - ESLint for Vue 3 + TypeScript
- `tsconfig.json` - TypeScript compiler options
- `vite.config.ts` - Vite configuration

### VS Code Integration
- `.vscode/settings.json` - Format on save, auto-fix
- `.vscode/extensions.json` - Recommended extensions

## Prettier Configuration

All projects share the same Prettier config:

```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

## ESLint Rules

### Auth Server (TypeScript)
- TypeScript recommended rules
- Prettier integration
- Unused vars as warnings
- No explicit any as warning

### Frontend (Vue 3 + TypeScript)
- Vue 3 recommended rules
- TypeScript recommended rules
- Prettier integration
- Multi-word component names allowed

## Ruff Configuration (Backend)

### Selected Rules
- **E/W**: pycodestyle errors and warnings
- **F**: pyflakes (undefined names, unused imports)
- **I**: isort (import sorting)
- **N**: pep8-naming conventions
- **UP**: pyupgrade (modern Python syntax)
- **B**: flake8-bugbear (common bugs)
- **C4**: flake8-comprehensions (list/dict comprehensions)
- **SIM**: flake8-simplify (simplification suggestions)
- **TCH**: flake8-type-checking (type-checking imports)
- **RUF**: ruff-specific rules

### Format Options
- Line length: 100
- Double quotes
- Space indentation (4 spaces)
- LF line endings

## Pre-commit Hooks

Install pre-commit hooks to automatically lint/format before commits:

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**What it does:**
- Runs Ruff on Python files
- Runs Prettier on TypeScript/Vue files
- Checks for trailing whitespace
- Ensures files end with newline
- Validates YAML/JSON syntax
- Prevents large file commits

## VS Code Integration

Install recommended extensions:
1. **Python**: Ruff (charliermarsh.ruff)
2. **TypeScript/JS**: ESLint (dbaeumer.vscode-eslint)
3. **Formatting**: Prettier (esbenp.prettier-vscode)
4. **Vue**: Volar (vue.volar)
5. **Tailwind**: Tailwind CSS IntelliSense

**Format on Save** is enabled automatically.

## Manual Formatting

### Auth Server
```bash
cd auth-server
pnpm run format
```

Formats all `.ts` files in `src/`

### Backend
```bash
cd backend
make format
# or
ruff format .
```

Formats all `.py` files

### Frontend
```bash
cd frontend
pnpm run format
```

Formats all `.vue`, `.ts`, `.css` files in `src/`

## Type Checking

### Auth Server
```bash
cd auth-server
tsc --noEmit
```

### Frontend
```bash
cd frontend
pnpm run type-check
```

### Backend
Type checking is built into Pydantic and FastAPI runtime.

## CI/CD Integration

Add to your CI pipeline:

```yaml
# Example GitHub Actions
- name: Lint Auth Server
  run: cd auth-server && pnpm run lint

- name: Lint Frontend
  run: cd frontend && pnpm run lint

- name: Lint Backend
  run: cd backend && ruff check .

- name: Check Formatting
  run: pnpm run format:check

- name: Type Check
  run: pnpm run type-check
```

## Ignoring Files

### Prettier (`.prettierignore`)
- `node_modules/`
- `dist/`, `build/`
- `__pycache__/`
- `.env` files

### ESLint
Automatically ignores `node_modules/`, `dist/`

### Ruff
Automatically ignores `__pycache__/`, `.venv/`, `venv/`

## Fixing Issues

### Auto-fix everything
```bash
# From root
pnpm run format        # Format all projects
pnpm run lint:auth -- --fix
pnpm run lint:frontend -- --fix
cd backend && make lint-fix
```

### Check before commit
```bash
pnpm run format:check  # Check formatting
pnpm run lint          # Check linting
pnpm run type-check    # Check types
```

## Customizing Rules

### ESLint
Edit `eslint.config.js` in auth-server or frontend:
```js
rules: {
  'your-rule': 'off',  // Disable rule
}
```

### Ruff
Edit `backend/.ruff.toml`:
```toml
[lint]
ignore = [
    "E501",  # Add rules to ignore
]
```

### Prettier
Edit `.prettierrc` in root:
```json
{
  "semi": false,
  "singleQuote": true
}
```

## Summary

All three services now have:
- ✅ Consistent linting rules
- ✅ Automatic formatting
- ✅ Type checking
- ✅ Pre-commit hooks
- ✅ VS Code integration
- ✅ CI/CD ready

Run `pnpm run format` from root to format everything at once!

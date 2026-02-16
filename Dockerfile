# Multi-stage build for FastAPI + Vue 3

# Stage 1: Build frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy root config files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy all package.json files to allow workspace install
COPY frontend/package.json ./frontend/
COPY auth-server/package.json ./auth-server/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy frontend source
COPY frontend/ ./frontend/

# Build frontend
RUN cd frontend && pnpm run build

# Stage 2: Build backend
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./static

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

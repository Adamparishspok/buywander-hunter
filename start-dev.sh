#!/bin/bash
# Start all three services for Better Auth + FastAPI + Vue 3 development

echo "Starting BuyWander Deal Hunter (Gigachad Stack + Better Auth)..."
echo ""
echo "This will start three services:"
echo "  - Auth Server (Better Auth) on http://localhost:3001"
echo "  - Backend API (FastAPI) on http://localhost:8000"
echo "  - Frontend (Vue 3 + TS) on http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Start auth server in background
(cd auth-server && pnpm run dev) &
AUTH_PID=$!
echo "Auth server started (PID: $AUTH_PID)"

# Wait a moment for auth server to start
sleep 3

# Start backend in background
(cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait a moment for backend to start
sleep 2

# Start frontend in background
(cd frontend && pnpm run dev) &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping all servers..."
    kill $AUTH_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Wait for all processes
wait

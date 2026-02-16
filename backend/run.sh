#!/bin/bash
# Run the FastAPI backend server with uvicorn

cd "$(dirname "$0")"
uvicorn main:app --reload --host 0.0.0.0 --port 8000

#!/bin/bash
# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set. Create a .env file with:"
  echo '  DATABASE_URL=postgresql://neondb_owner:<PASSWORD>@ep-nameless-mouse-af40upqp-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require'
  exit 1
fi

export SECRET_KEY="${SECRET_KEY:-supersecretkey}"

python3 web_app.py

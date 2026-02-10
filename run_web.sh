#!/bin/bash
# Set DATABASE_URL for local testing (update with your Neon connection string)
export DATABASE_URL="postgresql://neondb_owner:npg_QltRB7TGCb0r@ep-nameless-mouse-af40upqp-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
export SECRET_KEY="supersecretkey"

python3 web_app.py

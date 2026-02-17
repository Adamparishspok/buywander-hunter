#!/usr/bin/env python3
"""
Database initialization script for BuyWander.
Creates all necessary tables for both Better Auth and the FastAPI backend.

Better Auth uses TEXT ids (random strings), not SERIAL integers.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_tables_sync():
    """Create database tables using synchronous psycopg2."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            # Drop existing tables if they exist (for clean start)
            print("Dropping existing tables...")
            cur.execute('DROP TABLE IF EXISTS pull_items CASCADE;')
            cur.execute('DROP TABLE IF EXISTS scrape_history CASCADE;')
            cur.execute('DROP TABLE IF EXISTS scrape_items CASCADE;')
            cur.execute('DROP TABLE IF EXISTS users CASCADE;')
            cur.execute('DROP TABLE IF EXISTS verification CASCADE;')
            cur.execute('DROP TABLE IF EXISTS session CASCADE;')
            cur.execute('DROP TABLE IF EXISTS account CASCADE;')
            cur.execute('DROP TABLE IF EXISTS "user" CASCADE;')
            
            print("Creating user table...")
            # Better Auth uses TEXT ids, not SERIAL integers
            cur.execute("""
                CREATE TABLE "user" (
                    id TEXT NOT NULL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    "emailVerified" BOOLEAN DEFAULT FALSE,
                    image TEXT,
                    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            print("Creating account table...")
            cur.execute("""
                CREATE TABLE account (
                    id TEXT NOT NULL PRIMARY KEY,
                    "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    "accountId" TEXT NOT NULL,
                    "providerId" TEXT NOT NULL,
                    "accessToken" TEXT,
                    "refreshToken" TEXT,
                    "idToken" TEXT,
                    "accessTokenExpiresAt" TIMESTAMP,
                    "refreshTokenExpiresAt" TIMESTAMP,
                    scope TEXT,
                    password TEXT,
                    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            print("Creating session table...")
            cur.execute("""
                CREATE TABLE session (
                    id TEXT NOT NULL PRIMARY KEY,
                    "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    token TEXT UNIQUE NOT NULL,
                    "expiresAt" TIMESTAMP NOT NULL,
                    "ipAddress" TEXT,
                    "userAgent" TEXT,
                    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            print("Creating verification table...")
            cur.execute("""
                CREATE TABLE verification (
                    id TEXT NOT NULL PRIMARY KEY,
                    identifier TEXT NOT NULL,
                    value TEXT NOT NULL,
                    "expiresAt" TIMESTAMP NOT NULL,
                    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            print("Creating scrape_history table...")
            # Backend API tables - user_id references Better Auth user (TEXT)
            cur.execute("""
                CREATE TABLE scrape_history (
                    id SERIAL PRIMARY KEY,
                    pull_id VARCHAR(255) UNIQUE NOT NULL,
                    user_id TEXT REFERENCES "user"(id),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) NOT NULL,
                    items_found INTEGER DEFAULT 0,
                    error TEXT
                );
            """)
            
            print("Creating pull_items table...")
            cur.execute("""
                CREATE TABLE pull_items (
                    id SERIAL PRIMARY KEY,
                    pull_id VARCHAR(255) NOT NULL,
                    interest_category VARCHAR(255),
                    title TEXT,
                    retail VARCHAR(255),
                    current_bid VARCHAR(255),
                    bids INTEGER DEFAULT 0,
                    end_date VARCHAR(255),
                    url TEXT,
                    image_url TEXT,
                    deal_score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pull_id) REFERENCES scrape_history(pull_id) ON DELETE CASCADE
                );
            """)
            
            print("Creating indexes...")
            cur.execute('CREATE INDEX idx_user_email ON "user"(email);')
            cur.execute('CREATE INDEX idx_account_user_id ON account("userId");')
            cur.execute('CREATE INDEX idx_session_user_id ON session("userId");')
            cur.execute('CREATE INDEX idx_session_token ON session(token);')
            cur.execute("CREATE INDEX idx_scrape_history_user_id ON scrape_history(user_id);")
            cur.execute("CREATE INDEX idx_scrape_history_pull_id ON scrape_history(pull_id);")
            cur.execute("CREATE INDEX idx_pull_items_pull_id ON pull_items(pull_id);")
            
        conn.commit()
        print("Database tables created successfully!")
        
        # Show created tables
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            print("Tables: " + ", ".join([t[0] for t in tables]))
            
    except Exception as e:
        conn.rollback()
        print("Error creating tables: " + str(e))
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Initializing BuyWander database...")
    create_tables_sync()
    print("Done!")
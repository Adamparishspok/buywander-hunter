"""Database helpers for Neon Postgres."""
import os
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta


def get_connection():
    """Get a connection to the Neon database using DATABASE_URL env var."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return psycopg2.connect(database_url)


def save_pull_history(pull_id, timestamp, status, items_found, error=None, user_id=None):
    """Save a pull history entry."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO scrape_history (pull_id, timestamp, status, items_found, error, user_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (pull_id) DO UPDATE
                SET timestamp = EXCLUDED.timestamp,
                    status = EXCLUDED.status,
                    items_found = EXCLUDED.items_found,
                    error = EXCLUDED.error,
                    user_id = EXCLUDED.user_id
                """,
                (pull_id, timestamp, status, items_found, error, user_id),
            )
        conn.commit()
    finally:
        conn.close()


def save_pull_items(pull_id, items_list):
    """Bulk insert pull items. items_list should be a list of dicts with keys matching the CSV columns."""
    if not items_list:
        return
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Convert items to tuples for insertion
            rows = []
            for item in items_list:
                rows.append((
                    pull_id,
                    item.get("Interest Category"),
                    item.get("Title"),
                    item.get("Retail"),
                    item.get("Current Bid"),
                    item.get("Bids"),
                    item.get("End Date"),
                    item.get("URL"),
                    item.get("Image URL"),
                    item.get("Deal Score"),
                ))
            
            execute_batch(
                cur,
                """
                INSERT INTO pull_items 
                (pull_id, interest_category, title, retail, current_bid, bids, end_date, url, image_url, deal_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )
        conn.commit()
    finally:
        conn.close()


def load_history(user_id=None):
    """Load all pull history entries, ordered by pull_id desc (newest first)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if user_id:
                cur.execute(
                    """
                    SELECT pull_id, timestamp, status, items_found, error
                    FROM scrape_history
                    WHERE user_id = %s OR user_id IS NULL
                    ORDER BY pull_id DESC
                    LIMIT 50
                    """,
                    (user_id,)
                )
            else:
                cur.execute(
                    """
                    SELECT pull_id, timestamp, status, items_found, error
                    FROM scrape_history
                    ORDER BY pull_id DESC
                    LIMIT 50
                    """
                )
            rows = cur.fetchall()
            return [
                {
                    "pull_id": row[0],
                    "timestamp": row[1],
                    "status": row[2],
                    "items_found": row[3],
                    "error": row[4],
                }
                for row in rows
            ]
    finally:
        conn.close()


def load_pull_items(pull_id):
    """Load all items for a specific pull."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT interest_category, title, retail, current_bid, bids, 
                       end_date, url, image_url, deal_score
                FROM pull_items
                WHERE pull_id = %s
                """,
                (pull_id,),
            )
            rows = cur.fetchall()
            return [
                {
                    "Interest Category": row[0],
                    "Title": row[1],
                    "Retail": row[2],
                    "Current Bid": row[3],
                    "Bids": row[4],
                    "End Date": row[5],
                    "URL": row[6],
                    "Image URL": row[7],
                    "Deal Score": row[8],
                }
                for row in rows
            ]
    finally:
        conn.close()


def get_latest_pull(user_id=None):
    """Get the most recent successful pull and its items."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if user_id:
                cur.execute(
                    """
                    SELECT pull_id, timestamp, items_found
                    FROM scrape_history
                    WHERE status = 'success' AND (user_id = %s OR user_id IS NULL)
                    ORDER BY pull_id DESC
                    LIMIT 1
                    """,
                    (user_id,)
                )
            else:
                cur.execute(
                    """
                    SELECT pull_id, timestamp, items_found
                    FROM scrape_history
                    WHERE status = 'success'
                    ORDER BY pull_id DESC
                    LIMIT 1
                    """
                )
            row = cur.fetchone()
            if not row:
                return None, []
            
            pull_id, timestamp, items_found = row
            entry = {
                "pull_id": pull_id,
                "timestamp": timestamp,
                "items_found": items_found,
            }
            
            items = load_pull_items(pull_id)
            return entry, items
    finally:
        conn.close()


def cleanup_old_scrapes(days_old=2):
    """Delete scrape runs and their items older than the specified number of days.

    Args:
        days_old (int): Number of days old to consider for deletion (default: 2)

    Returns:
        dict: Summary of cleanup operations with counts of deleted items
    """
    cutoff_date = datetime.now() - timedelta(days=days_old)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # First, delete pull items for old scrapes
            cur.execute(
                """
                DELETE FROM pull_items
                WHERE pull_id IN (
                    SELECT pull_id FROM scrape_history
                    WHERE timestamp < %s
                )
                """,
                (cutoff_date,)
            )
            items_deleted = cur.rowcount

            # Then delete the scrape history entries
            cur.execute(
                """
                DELETE FROM scrape_history
                WHERE timestamp < %s
                """,
                (cutoff_date,)
            )
            history_deleted = cur.rowcount

        conn.commit()

        return {
            "items_deleted": items_deleted,
            "history_deleted": history_deleted,
            "cutoff_date": cutoff_date.isoformat(),
            "days_old": days_old
        }
    finally:
        conn.close()

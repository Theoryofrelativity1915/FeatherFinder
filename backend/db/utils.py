from backend.model.inference import CLASS_NAMES
import sqlite3
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(script_dir, "bird_tracker.db")

# Database setup
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    identifier_col_defs = [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "username TEXT UNIQUE",
        "bird_count INTEGER DEFAULT 0"
    ]
    class_col_defs = [f'{c.replace(" ", "_").replace("-", "_")} INTEGER DEFAULT 0' for c in CLASS_NAMES]
    all_col_defs = identifier_col_defs + class_col_defs
    all_col_defs_str = ",".join(all_col_defs)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            {all_col_defs_str}
        )
    """)
    conn.commit()
    conn.close()

def insert_user(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO users (username)
        VALUES (?) 
        ON CONFLICT(username) DO NOTHING
    """, (username,))
    conn.commit()
    conn.close()


def update_seen_birds(username, bird_name):
    bird_name = bird_name.replace(" ", "_").replace("-", "_")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE users
        SET 
            bird_count = bird_count + CASE WHEN {bird_name} = 0 THEN 1 ELSE 0 END,
            {bird_name} = 1
        WHERE username = ?
    """, (username,))
    conn.commit()
    conn.close()

def get_top_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, bird_count 
        FROM users 
        ORDER BY bird_count DESC LIMIT 5
    """)
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_stats(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rank, bird_count FROM (
            SELECT username, bird_count, RANK() 
            OVER (ORDER BY bird_count DESC) AS rank
            FROM users
        )
        WHERE username = ?;
    """, (username,))
    rank, bird_count = cursor.fetchall()[0]
    conn.close()
    return rank, bird_count
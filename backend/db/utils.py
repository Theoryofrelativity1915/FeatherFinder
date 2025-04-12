from backend.model.inference import CLASS_NAMES
from aws_advanced_python_wrapper import AwsWrapperConnection
from mysql.connector import Connect
import mysql.connector

config = {
    'user': 'admin',
    'password': 'TEFpwMMv3hV7RStxRPvC',
    'host': 'database-2.cluster-cqjc0a2s0ppn.us-east-1.rds.amazonaws.com',
    'port': 3306  # Default MySQL port
}

# Database setup
def init_db():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print('connected')

        identifier_col_defs = [
            "id INT AUTO_INCREMENT PRIMARY KEY",
            "username VARCHAR(255) UNIQUE",
            "bird_count INT DEFAULT 0"
        ]
        class_col_defs = [f'{c.replace(" ", "_").replace("-", "_")} INT DEFAULT 0' for c in CLASS_NAMES]
        all_col_defs = identifier_col_defs + class_col_defs
        all_col_defs_str = ",".join(all_col_defs)
        cursor.execute("USE bird_tracker")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                {all_col_defs_str}
            )
        """)
        conn.commit()
        print(f"Ensured users table exists. Rows affected: {cursor.rowcount}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("Connection closed")

def insert_user(username):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("USE bird_tracker")
    cursor.execute("""
        INSERT INTO users (username)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE username=username
    """, (username,))
    conn.commit()
    conn.close()


def update_seen_birds(username, bird_name):
    bird_name = bird_name.replace(" ", "_").replace("-", "_")
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("USE bird_tracker")
    cursor.execute(f"""
        UPDATE users
        SET
            bird_count = bird_count + IF({bird_name} = 0, 1, 0),
            {bird_name} = 1
        WHERE username = %s
    """, (username,))
    conn.commit()
    conn.close()

def get_top_users():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("USE bird_tracker")
    cursor.execute("""
        SELECT username, bird_count
        FROM users
        ORDER BY bird_count DESC LIMIT 5
    """)
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_stats(username):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("USE bird_tracker")
    cursor.execute("""
        SELECT rank_, bird_count FROM (
            SELECT username, bird_count, RANK()
            OVER (ORDER BY bird_count DESC) AS rank_
            FROM users
        ) AS user_ranks
        WHERE username = %s;
    """, (username,))
    rank, bird_count = cursor.fetchall()[0]
    conn.close()
    return rank, bird_count

# app/database.py
import pymysql
from pymysql import cursors
from pymysql.err import OperationalError
from config import CONFIG
    
def get_db_connection():
    """Create MySQL connection using TOML config"""
    return pymysql.connect(
        host=CONFIG["database"]["host"],
        user=CONFIG["database"]["user"],
        password=CONFIG["database"]["password"],
        database=CONFIG["database"]["dbname"],
        cursorclass=cursors.DictCursor
    )

# Initialize the database(only need once for creating table)
def init_db():
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id VARCHAR(36) PRIMARY KEY,
                    company_id VARCHAR(20) NOT NULL,
                    status ENUM('pending', 'success', 'failed') DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    report_path TEXT,
                    error_message TEXT
                )
            """)
        conn.commit()
    except OperationalError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
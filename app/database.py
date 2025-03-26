# app/database.py
import pymysql
from pymysql import cursors
from pymysql.err import OperationalError
import toml

def load_config(filepath="config.toml"):
    try:
        with open(filepath, 'r') as f:
            config = toml.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{filepath}' not found.")
        return None
    
def get_db_connection():
    config = load_config()
    if not config:
        return None
    db_config = config["MYSQL"]
    return pymysql.connect(
        host=db_config["HOST"],
        user=db_config["USER"],
        password=db_config["PASSWORD"],
        database=db_config["DATABASE"],
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
                    report_path TEXT
                )
            """)
        conn.commit()
    except OperationalError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
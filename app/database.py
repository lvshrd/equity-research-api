# app/database.py
import pymysql
from pymysql import cursors
from pymysql.err import OperationalError
import uuid
from passlib.context import CryptContext
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config_load import CONFIG

    
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
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    api_key VARCHAR(64) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            # Create tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id VARCHAR(36) PRIMARY KEY,
                    company_id VARCHAR(20) NOT NULL,
                    status ENUM('pending', 'success', 'failed') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    report_path TEXT,
                    error_message TEXT,
                    user_id VARCHAR(36) NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )          
            """)
            # Insert the admin user if it doesn't exist
            admin_username = CONFIG["app"]["DEFAULT_USERNAME"]
            admin_password = CONFIG["app"]["DEFAULT_PASSWORD"] 
            hashed_password = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(admin_password)
            admin_user_id = str(uuid.uuid4())
            admin_api_key = CONFIG["app"]["API_KEY"] 

            # Check if the admin user already exists
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (admin_username,))
            existing_admin = cursor.fetchone()

            if not existing_admin:
                cursor.execute("""
                    INSERT INTO users (user_id, username, password_hash, api_key)
                    VALUES (%s, %s, %s, %s)
                """, (admin_user_id, admin_username, hashed_password, admin_api_key))
                print(f"Admin user '{admin_username}' created.")
            else:
                print(f"Admin user '{admin_username}' already exists.")

        conn.commit()
    except OperationalError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
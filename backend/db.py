import mysql.connector
from mysql.connector import Error
import os
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from a .env file, if present.
# Prefer backend/.env, but also support a project-root .env when run from there.
BASE_DIR = Path(__file__).resolve().parent
ENV_PATHS = [BASE_DIR / '.env', BASE_DIR.parent / '.env']

for env_path in ENV_PATHS:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break
else:
    # No .env found; fall back to hard-coded defaults and guide the user.
    print(
        "[db.py] Warning: .env file not found in 'backend/' or project root. "
        "Using default DB settings (localhost/root/cmms_db). "
        "Create backend/.env with DB_HOST, DB_USER, DB_PASSWORD, DB_NAME to configure."
    )


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'cmms_db')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def is_db_initialized() -> bool:
    """Check whether the core application tables already exist.

    This is a *non-destructive* check used on startup to decide whether the
    schema needs to be initialized. If the connection fails or the check
    errors, it returns False.
    """

    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        # Use one core table as a representative check.
        cursor.execute("SHOW TABLES LIKE 'Person'")
        return cursor.fetchone() is not None
    except Error as e:
        print(f"Error checking database initialization: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def init_db():
    """Initializes the database with the schema in ``schema.sql``.

    WARNING: This function will execute all statements in ``backend/schema.sql``,
    including ``DROP TABLE IF EXISTS ...``. It is **destructive** and should be
    used only for initial setup or when you explicitly want to reset the
    database.
    """
    conn = get_db_connection()
    if conn is None:
        # Try connecting without database to create it
        try:
            conn = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', '')
            )
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME', 'cmms_db')}")
            print("Database created or already exists.")
            conn.close()
            conn = get_db_connection()
        except Error as e:
            print(f"Error creating database: {e}")
            return

    if conn:
        cursor = conn.cursor()
        schema_path = BASE_DIR / 'schema.sql'
        with open(schema_path, 'r') as f:
            schema = f.read()
            # Split by semicolon to execute multiple statements
            statements = schema.split(';')
            for statement in statements:
                if statement.strip():
                    try:
                        cursor.execute(statement)
                    except Error as e:
                        print(
                            f"Error executing statement: {statement[:50]}... -> {e}")
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully.")

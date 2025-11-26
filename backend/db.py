import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()


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


def init_db():
    """Initializes the database with the schema."""
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
        with open('backend/schema.sql', 'r') as f:
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


if __name__ == '__main__':
    init_db()

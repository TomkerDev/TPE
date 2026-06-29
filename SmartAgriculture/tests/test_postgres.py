import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

load_dotenv()

def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        connection = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("✓ PostgreSQL connection successful!")
        print(f"  Database version: {db_version[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except OperationalError as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False

if __name__ == "__main__":
    test_postgres_connection()
import psycopg2
from sqlalchemy import create_engine
import os

# Test 1: Direct psycopg2 connection
try:
    conn = psycopg2.connect(
        dbname="postgres",  # Connect to default database first
        user="postgres",
        password="password",
        host="localhost"
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Create database through psycopg2
    cur.execute("DROP DATABASE IF EXISTS test_db_2;")
    cur.execute("CREATE DATABASE test_db_2;")
    cur.close()
    conn.close()
    
    print("Database created successfully")
    
    # Test 2: SQLAlchemy connection
    engine = create_engine("postgresql://postgres:password@localhost:5432/test_db_2")
    with engine.connect() as connection:
        print("SQLAlchemy connection successful")
        
except Exception as e:
    print(f"Error: {e}")

# backend/database.py
import mysql.connector
from mysql.connector import pooling, Error
from config import DB_CONFIG

# Connection pool variable
db_pool = None

def initialize_pool():
    """Initialize the database connection pool"""
    global db_pool
    try:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="civic_pool",
            pool_size=5,  # Number of connections to keep open
            pool_reset_session=True,  # Reset session variables when returning connection
            **DB_CONFIG
        )
        print("Database connection pool created successfully.")
        return True
    except Error as e:
        print(f"Error creating database connection pool: {e}")
        db_pool = None
        return False

def get_db_connection():
    """Get a connection from the pool"""
    global db_pool
    
    if db_pool is None:
        if not initialize_pool():
            return None
    
    try:
        connection = db_pool.get_connection()
        return connection
    except Error as e:
        print(f"Error getting connection from pool: {e}")
        return None

def close_db_connection(connection):
    """Return a connection to the pool"""
    if connection and connection.is_connected():
        connection.close()  # This returns the connection to the pool

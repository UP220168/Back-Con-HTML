import os
from dotenv import load_dotenv
from mysql_connection_pool import MySQLConnectionPool
import traceback

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

project_root = os.path.join(os.path.dirname(__file__))
print(f"Project root: {project_root}")

# Database configuration with Docker support
database_name = os.environ.get("DB_NAME", "cinema_foraneo_db")
db_host = os.environ.get("DB_HOST_NAME", os.environ.get("MYSQL_HOST", "cinema_foraneo_sql"))
db_user = os.environ.get("DB_USER_NAME", "root")
db_password = os.environ.get("DB_PASSWORD", "root")
db_port = int(os.environ.get("DB_HOST_PORT", "3306"))

database = MySQLConnectionPool(
    host=db_host,
    user=db_user,
    password=db_password,
    database=database_name,
    pool_size=10,
    logs=os.path.join(project_root, "logs", "mysql_pool.log")
)

print("Root directory:", project_root)

try:
    exist = database.execute_safe(
        "SHOW DATABASES LIKE %s",
        (database_name,)
    )
    if len(exist) == 0:
        # Create the database
        database.execute_safe(f"CREATE DATABASE `{database_name}`")
        
        print(f"\n Database '{database_name}' created successfully\n")
        
        # Note: To create tables, you would need to connect to the specific database
        # and run the SQL files. This would require additional implementation.
        
    else:
        print(f"\n The database '{database_name}' already exists\n")
        
except Exception as e:
    print(f"\n Error with database operations: {e}\n")
    traceback.print_exc()
  
import os
from dotenv import load_dotenv
from mysql_connection_pool import MySQLConnectionPool
import traceback

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

project_root = os.path.join(os.path.dirname(__file__))
print(f"Project root: {project_root}")

database_name = os.environ.get("DB_NAME")

database = MySQLConnectionPool(
  host=os.environ.get("DB_HOST_NAME"),
  user=os.environ.get("DB_USER_NAME"),
  password=os.environ.get("DB_PASSWORD"),
  port=int(os.environ.get("DB_HOST_PORT")),
  pool_size=10,
  logs=os.path.join(project_root, "logs", "mysql_pool.log"),
  clear_logs=True
)

print("Root directory:", project_root)

try:
  exist = database.execute_safe(
    "SHOW DATABASES LIKE %s",
    database_name,
  )
  if len(exist) == 0:
    # Create the database
    database.execute_safe(
      f"CREATE DATABASE `{database_name}`"
    )
    
    # Switch to the created database
    database.switch_database(database_name)
    
    # Create tables and add base data in this order
    # database.run_multiple_sql_files_from_directory(project_root, [
    #   "sql/tb_auditorium.sql",
    #   "sql/tb_movie.sql",
    #   "sql/tb_employee.sql",
    #   "sql/tb_user.sql",
    #   "sql/tb_screening.sql",
    #   "sql/tb_ticket.sql",
    #   "sql/tb_sale.sql",
    # ])
    
    database.run_multiple_sql_files([
      "back/sql/tb_auditorium.sql",
      "back/sql/tb_movie.sql",
      "back/sql/tb_employee.sql",
      "back/sql/tb_user.sql",
      "back/sql/tb_screening.sql", #Aqui ya no jalo :(
      "back/sql/tb_ticket.sql",
      "back/sql/tb_sale.sql",
    ])
        
    # Insert initial data into the database
    admin_username = os.environ.get("ADMIN_USER_NAME")
    admin_password = os.environ.get("ADMIN_USER_PASSWORD")
    
    print("\n\n\n✅ Database created successfully 😃\n\n\n")
  else:
    database.execute_safe(
      "DROP DATABASE IF EXISTS `%s`",
      database_name
    )
    print("\n\n\n✅ The database already exists 😃\n\n\n")
except Exception as e:
  print("\n\n\n❌ Error creating the database 😞\n")
  print(f"Detalles del error: {e}")
  traceback.print_exc()
  
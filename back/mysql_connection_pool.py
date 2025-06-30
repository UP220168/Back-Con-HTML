import mysql.connector
from mysql.connector import pooling
import os
import logging
from typing import List, Dict, Any, Optional

class MySQLConnectionPool:
    def __init__(self, host: str, user: str, password: str, database: str = None, 
                 logs: str = None, pool_name: str = "mypool", pool_size: int = 5):
        """
        Initialize MySQL Connection Pool
        
        Args:
            host: Database host
            user: Database user
            password: Database password
            database: Database name (optional)
            logs: Log file path (optional)
            pool_name: Connection pool name
            pool_size: Maximum number of connections in pool
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.pool_name = pool_name
        self.pool_size = pool_size
        
        # Setup logging
        if logs:
            os.makedirs(os.path.dirname(logs), exist_ok=True)
            logging.basicConfig(
                filename=logs,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        
        self.logger = logging.getLogger(__name__)
        
        # Create connection pool
        self._create_pool()
    
    def _create_pool(self):
        """Create the MySQL connection pool"""
        try:
            config = {
                'host': self.host,
                'user': self.user,
                'password': self.password,
                'pool_name': self.pool_name,
                'pool_size': self.pool_size,
                'pool_reset_session': True,
                'autocommit': True
            }
            
            if self.database:
                config['database'] = self.database
                
            self.pool = pooling.MySQLConnectionPool(**config)
            self.logger.info(f"MySQL connection pool created successfully: {self.pool_name}")
            
        except mysql.connector.Error as e:
            self.logger.error(f"Error creating connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return self.pool.get_connection()
        except mysql.connector.Error as e:
            self.logger.error(f"Error getting connection from pool: {e}")
            raise
    
    def execute_safe(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a query safely with connection handling
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of dictionaries with query results
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('SHOW'):
                result = cursor.fetchall()
                self.logger.info(f"Query executed successfully: {query[:50]}...")
                return result
            else:
                # For INSERT, UPDATE, DELETE queries
                connection.commit()
                self.logger.info(f"Query executed successfully: {query[:50]}...")
                return []
                
        except mysql.connector.Error as e:
            self.logger.error(f"Database error: {e}")
            if connection:
                connection.rollback()
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """
        Execute multiple queries with the same statement
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            True if successful, False otherwise
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.executemany(query, params_list)
            connection.commit()
            
            self.logger.info(f"Batch query executed successfully: {len(params_list)} records")
            return True
            
        except mysql.connector.Error as e:
            self.logger.error(f"Database error in batch execution: {e}")
            if connection:
                connection.rollback()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error in batch execution: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def test_connection(self) -> bool:
        """Test if the connection pool is working"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result is not None
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def close_pool(self):
        """Close all connections in the pool"""
        try:
            # Note: mysql.connector pooling doesn't have a direct close_all method
            # Connections will be closed automatically when they go out of scope
            self.logger.info("Connection pool closed")
        except Exception as e:
            self.logger.error(f"Error closing connection pool: {e}")

"""
MandukyaDB - Main Database Class
Integrates all four states of consciousness into a unified API
"""

import os
from typing import List, Dict, Any, Union, Tuple, Optional
from .execution import ExecutionEngine
from .exceptions import MandukyaError

class MandukyaDB:
    """
    MandukyaDB - A lightweight relational database inspired by the Mandūkya Upaniṣad
    
    The four states of consciousness:
    - Jagrat (Waking): Storage layer - persistent data on disk
    - Swapna (Dreaming): Query planner - abstract query optimization  
    - Sushupti (Deep Sleep): Memory cache - fast in-memory operations
    - Turiya (Pure Consciousness): Execution engine - final query results
    """
    
    def __init__(self, database_path: str = ":memory:", cache_size: int = 1000):
        """
        Initialize MandukyaDB
        
        Args:
            database_path: Path to database file (":memory:" for in-memory database)
            cache_size: Size of the query result cache
        """
        if database_path == ":memory:":
            # Create temporary file for in-memory database
            import tempfile
            self.database_path = os.path.join(tempfile.gettempdir(), "mandukya_temp.db")
            self._is_memory = True
        else:
            self.database_path = database_path
            self._is_memory = False
        
        # Initialize the execution engine (Turiya) which coordinates all other layers
        self.engine = ExecutionEngine(self.database_path, cache_size)
        
    def execute(self, sql: str) -> Union[List[Tuple], int, str]:
        """
        Execute SQL statement
        
        Args:
            sql: SQL statement to execute
            
        Returns:
            For SELECT: List of tuples representing rows
            For INSERT: Row ID of inserted row
            For CREATE TABLE: Success message
            For DELETE: Number of deleted rows
        """
        try:
            return self.engine.execute(sql)
        except Exception as e:
            raise MandukyaError(str(e))
    
    def create_table(self, name: str, columns: List[Tuple[str, str]]) -> str:
        """
        Create a new table
        
        Args:
            name: Table name
            columns: List of (column_name, data_type) tuples
            
        Returns:
            Success message
        """
        column_defs = []
        for col_name, col_type in columns:
            column_defs.append(f"{col_name} {col_type}")
        
        sql = f"CREATE TABLE {name} ({', '.join(column_defs)})"
        return self.execute(sql)
    
    def insert(self, table: str, values: List[Any]) -> int:
        """
        Insert row into table
        
        Args:
            table: Table name
            values: List of values to insert
            
        Returns:
            Row ID of inserted row
        """
        value_strs = []
        for value in values:
            if isinstance(value, str):
                value_strs.append(f"'{value}'")
            else:
                value_strs.append(str(value))
        
        sql = f"INSERT INTO {table} VALUES ({', '.join(value_strs)})"
        return self.execute(sql)
    
    def select(self, table: str, columns: List[str] = None, where: Dict[str, Any] = None) -> List[Tuple]:
        """
        Select rows from table
        
        Args:
            table: Table name
            columns: List of column names (None for all columns)
            where: Dictionary with 'column', 'operator', 'value' keys
            
        Returns:
            List of tuples representing matching rows
        """
        if columns is None:
            columns_str = "*"
        else:
            columns_str = ", ".join(columns)
        
        sql = f"SELECT {columns_str} FROM {table}"
        
        if where:
            column = where['column']
            operator = where.get('operator', '=')
            value = where['value']
            
            if isinstance(value, str):
                value_str = f"'{value}'"
            else:
                value_str = str(value)
            
            sql += f" WHERE {column} {operator} {value_str}"
        
        return self.execute(sql)
    
    def delete(self, table: str, where: Dict[str, Any] = None) -> int:
        """
        Delete rows from table
        
        Args:
            table: Table name
            where: Dictionary with 'column', 'operator', 'value' keys
            
        Returns:
            Number of deleted rows
        """
        sql = f"DELETE FROM {table}"
        
        if where:
            column = where['column']
            operator = where.get('operator', '=')
            value = where['value']
            
            if isinstance(value, str):
                value_str = f"'{value}'"
            else:
                value_str = str(value)
            
            sql += f" WHERE {column} {operator} {value_str}"
        
        return self.execute(sql)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return self.engine.get_stats()
    
    def get_tables(self) -> List[str]:
        """Get list of table names"""
        stats = self.get_stats()
        return stats.get('tables', [])
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        self.engine.cleanup_cache()
    
    def commit(self):
        """Commit any pending changes to disk"""
        self.engine.storage.commit()
    
    def close(self):
        """Close database connection"""
        self.engine.close()
        
        # Clean up temporary file for in-memory databases
        if self._is_memory and os.path.exists(self.database_path):
            try:
                os.remove(self.database_path)
            except:
                pass  # Ignore cleanup errors
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __repr__(self):
        """String representation"""
        return f"MandukyaDB(path='{self.database_path}')"
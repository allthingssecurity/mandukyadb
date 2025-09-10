"""
Execution Engine - Turiya (Pure Consciousness State)
The final execution layer that coordinates all other components
"""

import hashlib
from typing import List, Dict, Any, Optional, Union, Tuple
from .parser import SQLParser, CreateTableStatement, InsertStatement, SelectStatement, DeleteStatement, DescribeStatement
from .storage import StorageEngine
from .cache import MemoryCache, MemoryEngine
from .exceptions import ExecutionError, ParseError, StorageError

class QueryOptimizer:
    """Simple query optimizer for better performance"""
    
    def __init__(self):
        pass
    
    def optimize_select(self, stmt: SelectStatement, table_metadata: Dict[str, Any]) -> SelectStatement:
        """Optimize SELECT statement"""
        # Simple optimization: if WHERE clause uses indexed column, note it
        if stmt.where_clause and 'indexes' in table_metadata:
            column = stmt.where_clause['column']
            if column in table_metadata['indexes']:
                # Mark as optimizable for index usage
                stmt.where_clause['_use_index'] = True
        
        return stmt

class ExecutionEngine:
    """Execution engine implementing the Turiya (Pure Consciousness) principle"""
    
    def __init__(self, database_path: str, cache_size: int = 1000):
        self.parser = SQLParser()
        self.storage = StorageEngine(database_path)
        self.cache = MemoryCache(cache_size)
        self.memory_engine = MemoryEngine(self.cache)
        self.optimizer = QueryOptimizer()
        
        # Execution statistics
        self.stats = {
            'queries_executed': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def execute(self, sql: str) -> Union[List[Tuple], int, str]:
        """Execute SQL statement and return results"""
        try:
            self.stats['queries_executed'] += 1
            
            # Parse SQL
            statement = self.parser.parse(sql)
            
            # Route to appropriate execution method
            if isinstance(statement, CreateTableStatement):
                return self._execute_create_table(statement)
            elif isinstance(statement, InsertStatement):
                return self._execute_insert(statement)
            elif isinstance(statement, SelectStatement):
                return self._execute_select(statement, sql)
            elif isinstance(statement, DeleteStatement):
                return self._execute_delete(statement)
            elif isinstance(statement, DescribeStatement):
                return self._execute_describe(statement)
            else:
                raise ExecutionError(f"Unsupported statement type: {type(statement)}")
                
        except ParseError as e:
            raise ExecutionError(f"Parse error: {e}")
        except StorageError as e:
            raise ExecutionError(f"Storage error: {e}")
        except Exception as e:
            raise ExecutionError(f"Execution error: {e}")
    
    def _execute_create_table(self, stmt: CreateTableStatement) -> str:
        """Execute CREATE TABLE statement"""
        self.storage.create_table(stmt.table_name, stmt.columns)
        
        # Cache table metadata
        metadata = {
            'columns': [{'name': col.name, 'type': col.data_type} for col in stmt.columns],
            'indexes': {}
        }
        self.cache.cache_table_metadata(stmt.table_name, metadata)
        
        return f"Table '{stmt.table_name}' created successfully"
    
    def _execute_insert(self, stmt: InsertStatement) -> int:
        """Execute INSERT statement"""
        table = self.storage.get_table(stmt.table_name)
        if not table:
            raise ExecutionError(f"Table '{stmt.table_name}' does not exist")
        
        row_id = table.insert_row(stmt.values)
        
        # Invalidate cache for this table
        self.cache.invalidate_table(stmt.table_name)
        self.memory_engine.invalidate_memory_table(stmt.table_name)
        
        # Persist changes
        self.storage.commit()
        
        return row_id
    
    def _execute_select(self, stmt: SelectStatement, original_sql: str) -> List[Tuple]:
        """Execute SELECT statement with caching"""
        # Generate query hash for caching
        query_hash = self._generate_query_hash(original_sql)
        
        # Check cache first
        cached_result = self.cache.get_query_result(query_hash)
        if cached_result is not None:
            self.stats['cache_hits'] += 1
            return self._format_select_result(cached_result, stmt.columns)
        
        self.stats['cache_misses'] += 1
        
        # Get table
        table = self.storage.get_table(stmt.table_name)
        if not table:
            raise ExecutionError(f"Table '{stmt.table_name}' does not exist")
        
        # Try in-memory table first
        memory_table = self.memory_engine.get_memory_table(stmt.table_name)
        if memory_table:
            rows = self._execute_select_memory(stmt, memory_table)
        else:
            # Execute on storage engine
            rows = self._execute_select_storage(stmt, table)
            
            # Load into memory for future queries if result set is reasonable size
            if len(rows) < 1000:  # Arbitrary threshold
                all_rows = table.select_all()
                self.memory_engine.load_table_into_memory(
                    stmt.table_name, all_rows, table.column_names
                )
        
        # Cache result
        self.cache.cache_query_result(query_hash, rows)
        
        return self._format_select_result(rows, stmt.columns)
    
    def _execute_select_memory(self, stmt: SelectStatement, memory_table) -> List[Dict[str, Any]]:
        """Execute SELECT on in-memory table"""
        if stmt.where_clause:
            return memory_table.select_where(
                stmt.where_clause['column'],
                stmt.where_clause['operator'], 
                stmt.where_clause['value']
            )
        else:
            return memory_table.select_all()
    
    def _execute_select_storage(self, stmt: SelectStatement, table) -> List[Dict[str, Any]]:
        """Execute SELECT on storage engine"""
        if stmt.where_clause:
            return table.select_where(
                stmt.where_clause['column'],
                stmt.where_clause['operator'],
                stmt.where_clause['value']
            )
        else:
            return table.select_all()
    
    def _execute_delete(self, stmt: DeleteStatement) -> int:
        """Execute DELETE statement"""
        table = self.storage.get_table(stmt.table_name)
        if not table:
            raise ExecutionError(f"Table '{stmt.table_name}' does not exist")
        
        if stmt.where_clause:
            deleted_count = table.delete_where(
                stmt.where_clause['column'],
                stmt.where_clause['operator'],
                stmt.where_clause['value']
            )
        else:
            # Delete all rows (dangerous!)
            all_rows = table.select_all()
            deleted_count = len(all_rows)
            for row in all_rows:
                row['__deleted__'] = True
        
        # Invalidate cache
        self.cache.invalidate_table(stmt.table_name)
        self.memory_engine.invalidate_memory_table(stmt.table_name)
        
        # Persist changes
        self.storage.commit()
        
        return deleted_count
    
    def _execute_describe(self, stmt: DescribeStatement) -> List[Tuple]:
        """Execute DESCRIBE statement"""
        table = self.storage.get_table(stmt.table_name)
        if not table:
            raise ExecutionError(f"Table '{stmt.table_name}' does not exist")
        
        # Return table schema as list of tuples (column_name, data_type, constraints)
        results = []
        for col in table.columns:
            constraints_str = " ".join(col.constraints) if col.constraints else ""
            results.append((col.name, col.data_type, constraints_str))
        
        return results
    
    def _generate_query_hash(self, sql: str) -> str:
        """Generate hash for query caching"""
        return hashlib.md5(sql.encode()).hexdigest()
    
    def _format_select_result(self, rows: List[Dict[str, Any]], columns: List[str]) -> List[Tuple]:
        """Format SELECT result as list of tuples"""
        result = []
        
        for row in rows:
            if '__deleted__' in row and row['__deleted__']:
                continue
                
            if columns == ['*']:
                # Return all columns (excluding internal ones)
                row_tuple = tuple(v for k, v in row.items() if not k.startswith('__'))
            else:
                # Return specified columns
                row_tuple = tuple(row.get(col) for col in columns)
            
            result.append(row_tuple)
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        cache_stats = self.cache.get_cache_stats()
        
        return {
            'execution_stats': self.stats,
            'cache_stats': cache_stats,
            'tables': list(self.storage.tables.keys())
        }
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        self.cache.cleanup()
    
    def close(self):
        """Close database connection and cleanup"""
        self.storage.commit()
        self.cleanup_cache()
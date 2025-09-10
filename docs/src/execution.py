"""
Execution Engine - Turiya (Pure Consciousness State)
"""

import hashlib
from typing import List, Dict, Any, Union, Tuple
from .parser import SQLParser, CreateTableStatement, InsertStatement, SelectStatement, DeleteStatement, DescribeStatement
from .storage import StorageEngine
from .cache import MemoryCache, MemoryEngine
from .exceptions import ExecutionError, ParseError, StorageError

class QueryOptimizer:
    def optimize_select(self, stmt: SelectStatement, table_metadata: Dict[str, Any]) -> SelectStatement:
        if stmt.where_clause and 'indexes' in table_metadata:
            column = stmt.where_clause['column']
            if column in table_metadata['indexes']:
                stmt.where_clause['_use_index'] = True
        return stmt

class ExecutionEngine:
    def __init__(self, database_path: str, cache_size: int = 1000):
        self.parser = SQLParser()
        self.storage = StorageEngine(database_path)
        self.cache = MemoryCache(cache_size)
        self.memory_engine = MemoryEngine(self.cache)
        self.optimizer = QueryOptimizer()
        self.stats = {'queries_executed': 0, 'cache_hits': 0, 'cache_misses': 0}

    def execute(self, sql: str) -> Union[List[Tuple], int, str]:
        try:
            self.stats['queries_executed'] += 1
            statement = self.parser.parse(sql)
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
        self.storage.create_table(stmt.table_name, stmt.columns)
        metadata = {'columns': [{'name': c.name, 'type': c.data_type} for c in stmt.columns], 'indexes': {}}
        self.cache.cache_table_metadata(stmt.table_name, metadata)
        return f"Table '{stmt.table_name}' created successfully"

    def _execute_insert(self, stmt: InsertStatement) -> int:
        table = self.storage.get_table(stmt.table_name)
        if not table:
            raise ExecutionError(f"Table '{stmt.table_name}' does not exist")
        row_id = table.insert_row(stmt.values)
        self.cache.invalidate_table(stmt.table_name)
        self.memory_engine.invalidate_memory_table(stmt.table_name)
        self.storage.commit()
        return row_id

    def _execute_select(self, stmt: SelectStatement, original_sql: str) -> List[Tuple]:
        query_hash = self._generate_query_hash(original_sql)
        cached = self.cache.get_query_result(query_hash)
        if cached is not None:
            self.stats['cache_hits'] += 1
            return self._format_select_result(cached, stmt.columns)
        self.stats['cache_misses'] += 1
        table = self.storage.get_table(stmt.table_name)
        if not table:
            raise ExecutionError(f"Table '{stmt.table_name}' does not exist")
        memory_table = self.memory_engine.get_memory_table(stmt.table_name)
        if memory_table:
            rows = self._execute_select_memory(stmt, memory_table)
        else:
            rows = self._execute_select_storage(stmt, table)
            if len(rows) < 1000:
                all_rows = table.select_all()
                self.memory_engine.load_table_into_memory(stmt.table_name, all_rows, table.column_names)
        self.cache.cache_query_result(query_hash, rows)
        return self._format_select_result(rows, stmt.columns)

    def _execute_select_memory(self, stmt: SelectStatement, memory_table) -> List[Dict[str, Any]]:
        if stmt.where_clause:
            return memory_table.select_where(stmt.where_clause['column'], stmt.where_clause['operator'], stmt.where_clause['value'])
        return memory_table.select_all()

    def _execute_select_storage(self, stmt: SelectStatement, table) -> List[Dict[str, Any]]:
        if stmt.where_clause:
            return table.select_where(stmt.where_clause['column'], stmt.where_clause['operator'], stmt.where_clause['value'])
        return table.select_all()

    def _execute_delete(self, stmt: DeleteStatement) -> int:
        table = self.storage.get_table(stmt.table_name)
        if not table:
            raise ExecutionError(f"Table '{stmt.table_name}' does not exist")
        if stmt.where_clause:
            deleted_count = table.delete_where(stmt.where_clause['column'], stmt.where_clause['operator'], stmt.where_clause['value'])
        else:
            all_rows = table.select_all()
            deleted_count = len(all_rows)
            for row in all_rows:
                row['__deleted__'] = True
        self.cache.invalidate_table(stmt.table_name)
        self.memory_engine.invalidate_memory_table(stmt.table_name)
        self.storage.commit()
        return deleted_count

    def _execute_describe(self, stmt: DescribeStatement) -> List[Tuple]:
        table = self.storage.get_table(stmt.table_name)
        if not table:
            raise ExecutionError(f"Table '{stmt.table_name}' does not exist")
        results = []
        for col in table.columns:
            constraints_str = " ".join(col.constraints) if col.constraints else ""
            results.append((col.name, col.data_type, constraints_str))
        return results

    def _generate_query_hash(self, sql: str) -> str:
        return hashlib.md5(sql.encode()).hexdigest()

    def _format_select_result(self, rows: List[Dict[str, Any]], columns: List[str]) -> List[Tuple]:
        result: List[Tuple] = []
        for row in rows:
            if '__deleted__' in row and row['__deleted__']:
                continue
            if columns == ['*']:
                row_tuple = tuple(v for k, v in row.items() if not k.startswith('__'))
            else:
                row_tuple = tuple(row.get(col) for col in columns)
            result.append(row_tuple)
        return result

    def get_stats(self) -> Dict[str, Any]:
        cache_stats = self.cache.get_cache_stats()
        return {'execution_stats': self.stats, 'cache_stats': cache_stats, 'tables': list(self.storage.tables.keys())}

    def cleanup_cache(self):
        self.cache.cleanup()

    def close(self):
        self.storage.commit()
        self.cleanup_cache()


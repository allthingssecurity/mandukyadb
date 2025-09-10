"""
MandukyaDB - Main Database Class
"""

import os
from typing import List, Dict, Any, Union, Tuple
from .execution import ExecutionEngine
from .exceptions import MandukyaError

class MandukyaDB:
    def __init__(self, database_path: str = ":memory:", cache_size: int = 1000):
        if database_path == ":memory:":
            import tempfile
            self.database_path = os.path.join(tempfile.gettempdir(), "mandukya_temp.db")
            self._is_memory = True
        else:
            self.database_path = database_path
            self._is_memory = False
        self.engine = ExecutionEngine(self.database_path, cache_size)

    def execute(self, sql: str) -> Union[List[Tuple], int, str]:
        try:
            return self.engine.execute(sql)
        except Exception as e:
            raise MandukyaError(str(e))

    def create_table(self, name: str, columns: List[Tuple[str, str]]) -> str:
        column_defs = [f"{c} {t}" for c, t in columns]
        sql = f"CREATE TABLE {name} ({', '.join(column_defs)})"
        return self.execute(sql)

    def insert(self, table: str, values: List[Any]) -> int:
        value_strs = [f"'{v}'" if isinstance(v, str) else str(v) for v in values]
        sql = f"INSERT INTO {table} VALUES ({', '.join(value_strs)})"
        return self.execute(sql)

    def select(self, table: str, columns: List[str] = None, where: Dict[str, Any] = None) -> List[Tuple]:
        columns_str = "*" if columns is None else ", ".join(columns)
        sql = f"SELECT {columns_str} FROM {table}"
        if where:
            col = where['column']; op = where.get('operator','='); val = where['value']
            val_str = f"'{val}'" if isinstance(val, str) else str(val)
            sql += f" WHERE {col} {op} {val_str}"
        return self.execute(sql)

    def delete(self, table: str, where: Dict[str, Any] = None) -> int:
        sql = f"DELETE FROM {table}"
        if where:
            col = where['column']; op = where.get('operator','='); val = where['value']
            val_str = f"'{val}'" if isinstance(val, str) else str(val)
            sql += f" WHERE {col} {op} {val_str}"
        return self.execute(sql)

    def get_stats(self) -> Dict[str, Any]:
        return self.engine.get_stats()

    def get_tables(self) -> List[str]:
        return self.get_stats().get('tables', [])

    def cleanup_cache(self):
        self.engine.cleanup_cache()

    def commit(self):
        self.engine.storage.commit()

    def close(self):
        self.engine.close()
        if self._is_memory and os.path.exists(self.database_path):
            try:
                os.remove(self.database_path)
            except:
                pass

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    def __repr__(self):
        return f"MandukyaDB(path='{self.database_path}')"


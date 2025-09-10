"""
Memory Cache Engine - Sushupti (Deep Sleep State)
Handles fast in-memory caching and operations
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import OrderedDict
import time
from .exceptions import StorageError

class CacheEntry:
    def __init__(self, data: Any, ttl: int = 300):
        self.data = data
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl
    def access(self):
        self.access_count += 1

class LRUCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        entry = self.cache[key]
        if entry.is_expired():
            del self.cache[key]
            return None
        self.cache.move_to_end(key)
        entry.access()
        return entry.data
    def put(self, key: str, value: Any, ttl: int = 300):
        if key in self.cache:
            self.cache[key] = CacheEntry(value, ttl)
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            self.cache[key] = CacheEntry(value, ttl)
    def invalidate(self, pattern: str = None):
        if pattern is None:
            self.cache.clear()
        else:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
    def cleanup_expired(self):
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]
        for key in expired_keys:
            del self.cache[key]

class MemoryCache:
    def __init__(self, max_size: int = 1000):
        self.query_cache = LRUCache(max_size)
        self.table_cache = LRUCache(max_size // 10)
        self.stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    def get_query_result(self, query_hash: str) -> Optional[List[Dict[str, Any]]]:
        result = self.query_cache.get(query_hash)
        if result is not None:
            self.stats['hits'] += 1
            return result
        else:
            self.stats['misses'] += 1
            return None
    def cache_query_result(self, query_hash: str, result: List[Dict[str, Any]], ttl: int = 300):
        self.query_cache.put(query_hash, result, ttl)
    def get_table_metadata(self, table_name: str) -> Optional[Dict[str, Any]]:
        return self.table_cache.get(f"table_meta_{table_name}")
    def cache_table_metadata(self, table_name: str, metadata: Dict[str, Any]):
        self.table_cache.put(f"table_meta_{table_name}", metadata, ttl=3600)
    def invalidate_table(self, table_name: str):
        self.query_cache.invalidate(table_name)
        self.table_cache.invalidate(f"table_meta_{table_name}")
    def cleanup(self):
        self.query_cache.cleanup_expired()
        self.table_cache.cleanup_expired()
    def get_cache_stats(self) -> Dict[str, Any]:
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': f"{hit_rate:.2f}%",
            'query_cache_size': len(self.query_cache.cache),
            'table_cache_size': len(self.table_cache.cache)
        }

class InMemoryTable:
    def __init__(self, name: str, columns: List[str], rows: List[Dict[str, Any]]):
        self.name = name
        self.columns = columns
        self.rows = rows
        self.indexes = {}
        self._build_indexes()
    def _build_indexes(self):
        for col in self.columns:
            self.indexes[col] = {}
            for i, row in enumerate(self.rows):
                if col in row and '__deleted__' not in row:
                    value = row[col]
                    if value not in self.indexes[col]:
                        self.indexes[col][value] = []
                    self.indexes[col][value].append(i)
    def select_all(self) -> List[Dict[str, Any]]:
        return [row for row in self.rows if '__deleted__' not in row]
    def select_where(self, column: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        if operator == '=' and column in self.indexes and value in self.indexes[column]:
            row_indices = self.indexes[column][value]
            return [self.rows[i] for i in row_indices if '__deleted__' not in self.rows[i]]
        else:
            results = []
            for row in self.rows:
                if '__deleted__' in row:
                    continue
                if self._evaluate_condition(row, column, operator, value):
                    results.append(row)
            return results
    def _evaluate_condition(self, row: Dict[str, Any], column: str, operator: str, value: Any) -> bool:
        if column not in row:
            return False
        row_value = row[column]
        if operator == '=':
            return row_value == value
        elif operator == '!=':
            return row_value != value
        elif operator == '<':
            return row_value < value
        elif operator == '<=':
            return row_value <= value
        elif operator == '>':
            return row_value > value
        elif operator == '>=':
            return row_value >= value
        else:
            return False

class MemoryEngine:
    def __init__(self, cache: MemoryCache):
        self.cache = cache
        self.memory_tables = {}
    def load_table_into_memory(self, table_name: str, rows: List[Dict[str, Any]], columns: List[str]):
        self.memory_tables[table_name] = InMemoryTable(table_name, columns, rows)
    def get_memory_table(self, table_name: str) -> Optional[InMemoryTable]:
        return self.memory_tables.get(table_name)
    def invalidate_memory_table(self, table_name: str):
        if table_name in self.memory_tables:
            del self.memory_tables[table_name]


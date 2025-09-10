"""
Memory Cache Engine - Sushupti (Deep Sleep State)
Handles fast in-memory caching and operations
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import OrderedDict
import time
from .exceptions import StorageError

class CacheEntry:
    """Represents a cached query result"""
    
    def __init__(self, data: Any, ttl: int = 300):  # 5 minute default TTL
        self.data = data
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return time.time() - self.created_at > self.ttl
    
    def access(self):
        """Record access to this cache entry"""
        self.access_count += 1

class LRUCache:
    """Least Recently Used cache implementation"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if entry.is_expired():
            del self.cache[key]
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        entry.access()
        
        return entry.data
    
    def put(self, key: str, value: Any, ttl: int = 300):
        """Put item in cache"""
        if key in self.cache:
            # Update existing entry
            self.cache[key] = CacheEntry(value, ttl)
            self.cache.move_to_end(key)
        else:
            # Add new entry
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                self.cache.popitem(last=False)
            
            self.cache[key] = CacheEntry(value, ttl)
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries"""
        if pattern is None:
            # Clear all
            self.cache.clear()
        else:
            # Remove entries matching pattern
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]

class MemoryCache:
    """Memory cache engine implementing the Sushupti (Deep Sleep) principle"""
    
    def __init__(self, max_size: int = 1000):
        self.query_cache = LRUCache(max_size)
        self.table_cache = LRUCache(max_size // 10)  # Smaller cache for table metadata
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def get_query_result(self, query_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached query result"""
        result = self.query_cache.get(query_hash)
        if result is not None:
            self.stats['hits'] += 1
            return result
        else:
            self.stats['misses'] += 1
            return None
    
    def cache_query_result(self, query_hash: str, result: List[Dict[str, Any]], ttl: int = 300):
        """Cache query result"""
        self.query_cache.put(query_hash, result, ttl)
    
    def get_table_metadata(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get cached table metadata"""
        return self.table_cache.get(f"table_meta_{table_name}")
    
    def cache_table_metadata(self, table_name: str, metadata: Dict[str, Any]):
        """Cache table metadata"""
        self.table_cache.put(f"table_meta_{table_name}", metadata, ttl=3600)  # 1 hour TTL
    
    def invalidate_table(self, table_name: str):
        """Invalidate all cache entries for a table"""
        self.query_cache.invalidate(table_name)
        self.table_cache.invalidate(f"table_meta_{table_name}")
    
    def cleanup(self):
        """Clean up expired entries"""
        self.query_cache.cleanup_expired()
        self.table_cache.cleanup_expired()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
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
    """In-memory representation of a table for fast operations"""
    
    def __init__(self, name: str, columns: List[str], rows: List[Dict[str, Any]]):
        self.name = name
        self.columns = columns
        self.rows = rows
        self.indexes = {}
        self._build_indexes()
    
    def _build_indexes(self):
        """Build in-memory indexes for fast lookups"""
        for col in self.columns:
            self.indexes[col] = {}
            for i, row in enumerate(self.rows):
                if col in row and '__deleted__' not in row:
                    value = row[col]
                    if value not in self.indexes[col]:
                        self.indexes[col][value] = []
                    self.indexes[col][value].append(i)
    
    def select_all(self) -> List[Dict[str, Any]]:
        """Select all non-deleted rows"""
        return [row for row in self.rows if '__deleted__' not in row]
    
    def select_where(self, column: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        """Select rows matching condition using indexes when possible"""
        if operator == '=' and column in self.indexes and value in self.indexes[column]:
            # Use index for exact match
            row_indices = self.indexes[column][value]
            return [self.rows[i] for i in row_indices if '__deleted__' not in self.rows[i]]
        else:
            # Full scan
            results = []
            for row in self.rows:
                if '__deleted__' in row:
                    continue
                if self._evaluate_condition(row, column, operator, value):
                    results.append(row)
            return results
    
    def _evaluate_condition(self, row: Dict[str, Any], column: str, operator: str, value: Any) -> bool:
        """Evaluate WHERE condition"""
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
    """Memory engine for fast in-memory table operations"""
    
    def __init__(self, cache: MemoryCache):
        self.cache = cache
        self.memory_tables = {}
    
    def load_table_into_memory(self, table_name: str, rows: List[Dict[str, Any]], columns: List[str]):
        """Load table data into memory for fast access"""
        self.memory_tables[table_name] = InMemoryTable(table_name, columns, rows)
    
    def get_memory_table(self, table_name: str) -> Optional[InMemoryTable]:
        """Get in-memory table if available"""
        return self.memory_tables.get(table_name)
    
    def invalidate_memory_table(self, table_name: str):
        """Remove table from memory"""
        if table_name in self.memory_tables:
            del self.memory_tables[table_name]
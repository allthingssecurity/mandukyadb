"""
Storage Engine - Jagrat (Waking State)
Handles persistent data storage with B+ trees
"""

import os
import pickle
import struct
from typing import List, Dict, Any, Optional, Tuple
from .exceptions import StorageError
from .parser import Column

class BTreeNode:
    """B+ tree node for efficient data storage and retrieval"""
    
    def __init__(self, is_leaf=False, order=4):
        self.is_leaf = is_leaf
        self.keys = []
        self.values = []  # Only used in leaf nodes
        self.children = []  # Only used in internal nodes
        self.next_leaf = None  # Pointer to next leaf for range queries
        self.order = order
    
    def is_full(self):
        return len(self.keys) >= self.order - 1
    
    def insert_key(self, key, value=None):
        """Insert key-value pair maintaining sorted order"""
        pos = 0
        while pos < len(self.keys) and self.keys[pos] < key:
            pos += 1
        
        self.keys.insert(pos, key)
        if self.is_leaf:
            self.values.insert(pos, value)
    
    def split(self):
        """Split node when it becomes full"""
        mid = len(self.keys) // 2
        new_node = BTreeNode(self.is_leaf, self.order)
        
        if self.is_leaf:
            new_node.keys = self.keys[mid:]
            new_node.values = self.values[mid:]
            new_node.next_leaf = self.next_leaf
            self.next_leaf = new_node
            
            self.keys = self.keys[:mid]
            self.values = self.values[:mid]
            
            return new_node.keys[0], new_node
        else:
            new_node.keys = self.keys[mid + 1:]
            new_node.children = self.children[mid + 1:]
            
            promoted_key = self.keys[mid]
            self.keys = self.keys[:mid]
            self.children = self.children[:mid + 1]
            
            return promoted_key, new_node

class BTree:
    """B+ tree implementation for table storage"""
    
    def __init__(self, order=4):
        self.root = BTreeNode(is_leaf=True, order=order)
        self.order = order
    
    def insert(self, key, value):
        """Insert key-value pair into B+ tree"""
        if self.root.is_full():
            new_root = BTreeNode(is_leaf=False, order=self.order)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        
        self._insert_non_full(self.root, key, value)
    
    def _insert_non_full(self, node, key, value):
        """Insert into a non-full node"""
        if node.is_leaf:
            node.insert_key(key, value)
        else:
            # Find child to insert into
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            if node.children[i].is_full():
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key, value)
    
    def _split_child(self, parent, index):
        """Split a full child node"""
        child = parent.children[index]
        promoted_key, new_child = child.split()
        
        parent.keys.insert(index, promoted_key)
        parent.children.insert(index + 1, new_child)
    
    def search(self, key):
        """Search for a key in the B+ tree"""
        return self._search_node(self.root, key)
    
    def _search_node(self, node, key):
        """Search for key starting from given node"""
        if node.is_leaf:
            for i, k in enumerate(node.keys):
                if k == key:
                    return node.values[i]
            return None
        else:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            return self._search_node(node.children[i], key)
    
    def range_query(self, start_key=None, end_key=None):
        """Perform range query returning all values in range"""
        results = []
        leaf = self._find_leftmost_leaf()
        
        while leaf:
            for i, key in enumerate(leaf.keys):
                if start_key is not None and key < start_key:
                    continue
                if end_key is not None and key > end_key:
                    return results
                results.append((key, leaf.values[i]))
            leaf = leaf.next_leaf
        
        return results
    
    def _find_leftmost_leaf(self):
        """Find the leftmost leaf node"""
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        return node

class Table:
    """Represents a database table with its schema and data"""
    
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = columns
        self.column_names = [col.name for col in columns]
        self.column_types = {col.name: col.data_type for col in columns}
        
        # B+ tree for primary storage (using row_id as key)
        self.data_tree = BTree()
        self.next_row_id = 1
        
        # Indexes for fast lookups (simplified - one per column)
        self.indexes = {}
    
    def insert_row(self, values: List[Any]) -> int:
        """Insert a row and return the row ID"""
        if len(values) != len(self.columns):
            raise StorageError(f"Expected {len(self.columns)} values, got {len(values)}")
        
        # Create row dictionary
        row = dict(zip(self.column_names, values))
        row_id = self.next_row_id
        self.next_row_id += 1
        
        # Store in main B+ tree
        self.data_tree.insert(row_id, row)
        
        # Update indexes
        for col_name, value in row.items():
            if col_name not in self.indexes:
                self.indexes[col_name] = BTree()
            self.indexes[col_name].insert(value, row_id)
        
        return row_id
    
    def select_all(self) -> List[Dict[str, Any]]:
        """Select all rows from table"""
        results = []
        for key, row in self.data_tree.range_query():
            results.append(row)
        return results
    
    def select_where(self, column: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        """Select rows matching WHERE clause"""
        results = []
        
        if operator == '=' and column in self.indexes:
            # Use index for exact match
            row_id = self.indexes[column].search(value)
            if row_id:
                row = self.data_tree.search(row_id)
                if row:
                    results.append(row)
        else:
            # Full table scan
            for key, row in self.data_tree.range_query():
                if self._evaluate_condition(row, column, operator, value):
                    results.append(row)
        
        return results
    
    def delete_where(self, column: str, operator: str, value: Any) -> int:
        """Delete rows matching WHERE clause, return count"""
        # For simplicity, we'll mark rows as deleted rather than actually removing them
        # In a full implementation, we'd need proper deletion with tree rebalancing
        deleted_count = 0
        
        for key, row in self.data_tree.range_query():
            if self._evaluate_condition(row, column, operator, value):
                # Mark as deleted (simplified approach)
                row['__deleted__'] = True
                deleted_count += 1
        
        return deleted_count
    
    def _evaluate_condition(self, row: Dict[str, Any], column: str, operator: str, value: Any) -> bool:
        """Evaluate WHERE condition against a row"""
        if '__deleted__' in row and row['__deleted__']:
            return False
            
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

class StorageEngine:
    """Storage engine implementing the Jagrat (Waking) principle"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.tables = {}
        self._load_database()
    
    def create_table(self, name: str, columns: List[Column]):
        """Create a new table"""
        if name in self.tables:
            raise StorageError(f"Table {name} already exists")
        
        self.tables[name] = Table(name, columns)
        self._save_database()
    
    def get_table(self, name: str) -> Optional[Table]:
        """Get table by name"""
        return self.tables.get(name)
    
    def table_exists(self, name: str) -> bool:
        """Check if table exists"""
        return name in self.tables
    
    def _load_database(self):
        """Load database from disk if a valid non-empty file exists."""
        if os.path.exists(self.database_path) and os.path.getsize(self.database_path) > 0:
            try:
                with open(self.database_path, 'rb') as f:
                    self.tables = pickle.load(f)
            except Exception as e:
                raise StorageError(f"Failed to load database: {e}")
        else:
            self.tables = {}
    
    def _save_database(self):
        """Save database to disk"""
        try:
            # Ensure directory exists
            dir_path = os.path.dirname(self.database_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            with open(self.database_path, 'wb') as f:
                pickle.dump(self.tables, f)
        except Exception as e:
            raise StorageError(f"Failed to save database: {e}")
    
    def commit(self):
        """Persist changes to disk"""
        self._save_database()

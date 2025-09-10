"""
Storage Engine - Jagrat (Waking State)
Handles persistent data storage with B+ trees
"""

import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
from .exceptions import StorageError
from .parser import Column

class BTreeNode:
    def __init__(self, is_leaf=False, order=4):
        self.is_leaf = is_leaf
        self.keys = []
        self.values = []
        self.children = []
        self.next_leaf = None
        self.order = order
    def is_full(self):
        return len(self.keys) >= self.order - 1
    def insert_key(self, key, value=None):
        pos = 0
        while pos < len(self.keys) and self.keys[pos] < key:
            pos += 1
        self.keys.insert(pos, key)
        if self.is_leaf:
            self.values.insert(pos, value)
    def split(self):
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
    def __init__(self, order=4):
        self.root = BTreeNode(is_leaf=True, order=order)
        self.order = order
    def insert(self, key, value):
        if self.root.is_full():
            new_root = BTreeNode(is_leaf=False, order=self.order)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key, value)
    def _insert_non_full(self, node, key, value):
        if node.is_leaf:
            node.insert_key(key, value)
        else:
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
        child = parent.children[index]
        promoted_key, new_child = child.split()
        parent.keys.insert(index, promoted_key)
        parent.children.insert(index + 1, new_child)
    def search(self, key):
        return self._search_node(self.root, key)
    def _search_node(self, node, key):
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
        results = []
        leaf = self._find_leftmost_leaf()
        while leaf:
            for i, key in enumerate(leaf.keys):
                if (start_key is None or key >= start_key) and (end_key is None or key <= end_key):
                    results.append((key, leaf.values[i]))
            leaf = leaf.next_leaf
        return results
    def _find_leftmost_leaf(self):
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        return node

class Table:
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = columns
        self.column_names = [col.name for col in columns]
        self.column_types = {col.name: col.data_type for col in columns}
        self.data_tree = BTree()
        self.next_row_id = 1
        self.indexes = {}
    def insert_row(self, values: List[Any]) -> int:
        if len(values) != len(self.columns):
            raise StorageError(f"Expected {len(self.columns)} values, got {len(values)}")
        row = dict(zip(self.column_names, values))
        row_id = self.next_row_id; self.next_row_id += 1
        self.data_tree.insert(row_id, row)
        for col_name, value in row.items():
            if col_name not in self.indexes:
                self.indexes[col_name] = BTree()
            self.indexes[col_name].insert(value, row_id)
        return row_id
    def select_all(self) -> List[Dict[str, Any]]:
        return [row for key, row in self.data_tree.range_query()]
    def select_where(self, column: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        results = []
        if operator == '=' and column in self.indexes:
            row_id = self.indexes[column].search(value)
            if row_id:
                row = self.data_tree.search(row_id)
                if row:
                    results.append(row)
        else:
            for key, row in self.data_tree.range_query():
                if self._evaluate_condition(row, column, operator, value):
                    results.append(row)
        return results
    def delete_where(self, column: str, operator: str, value: Any) -> int:
        deleted = 0
        for key, row in self.data_tree.range_query():
            if self._evaluate_condition(row, column, operator, value):
                row['__deleted__'] = True
                deleted += 1
        return deleted
    def _evaluate_condition(self, row: Dict[str, Any], column: str, operator: str, value: Any) -> bool:
        if '__deleted__' in row and row['__deleted__']:
            return False
        if column not in row:
            return False
        rv = row[column]
        if operator == '=': return rv == value
        if operator == '!=': return rv != value
        if operator == '<': return rv < value
        if operator == '<=': return rv <= value
        if operator == '>': return rv > value
        if operator == '>=': return rv >= value
        return False

class StorageEngine:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.tables = {}
        self._load_database()
    def create_table(self, name: str, columns: List[Column]):
        if name in self.tables:
            raise StorageError(f"Table {name} already exists")
        self.tables[name] = Table(name, columns)
        self._save_database()
    def get_table(self, name: str) -> Optional[Table]:
        return self.tables.get(name)
    def table_exists(self, name: str) -> bool:
        return name in self.tables
    def _load_database(self):
        if os.path.exists(self.database_path) and os.path.getsize(self.database_path) > 0:
            try:
                with open(self.database_path, 'rb') as f:
                    self.tables = pickle.load(f)
            except Exception as e:
                raise StorageError(f"Failed to load database: {e}")
        else:
            self.tables = {}
    def _save_database(self):
        try:
            dir_path = os.path.dirname(self.database_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            with open(self.database_path, 'wb') as f:
                pickle.dump(self.tables, f)
        except Exception as e:
            raise StorageError(f"Failed to save database: {e}")
    def commit(self):
        self._save_database()


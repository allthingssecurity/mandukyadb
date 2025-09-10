#!/usr/bin/env python3
"""
Test suite for MandukyaDB
"""

import sys
import os
import unittest
import tempfile
import shutil

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.mandukya_db import MandukyaDB
from src.exceptions import MandukyaError, ParseError
from src.parser import SQLParser, Column
from src.storage import BTree, StorageEngine

class TestSQLParser(unittest.TestCase):
    """Test SQL parser functionality"""
    
    def setUp(self):
        self.parser = SQLParser()
    
    def test_create_table_parsing(self):
        """Test CREATE TABLE statement parsing"""
        sql = "CREATE TABLE students (id INTEGER, name TEXT)"
        stmt = self.parser.parse(sql)
        
        self.assertEqual(stmt.table_name, "students")
        self.assertEqual(len(stmt.columns), 2)
        self.assertEqual(stmt.columns[0].name, "id")
        self.assertEqual(stmt.columns[0].data_type, "INTEGER")
        self.assertEqual(stmt.columns[1].name, "name")
        self.assertEqual(stmt.columns[1].data_type, "TEXT")
    
    def test_insert_parsing(self):
        """Test INSERT statement parsing"""
        sql = "INSERT INTO students VALUES (1, 'Arjuna')"
        stmt = self.parser.parse(sql)
        
        self.assertEqual(stmt.table_name, "students")
        self.assertEqual(stmt.values, [1, "Arjuna"])
    
    def test_select_parsing(self):
        """Test SELECT statement parsing"""
        sql = "SELECT * FROM students"
        stmt = self.parser.parse(sql)
        
        self.assertEqual(stmt.columns, ["*"])
        self.assertEqual(stmt.table_name, "students")
        self.assertIsNone(stmt.where_clause)
    
    def test_select_with_where(self):
        """Test SELECT with WHERE clause"""
        sql = "SELECT name FROM students WHERE id = 1"
        stmt = self.parser.parse(sql)
        
        self.assertEqual(stmt.columns, ["name"])
        self.assertEqual(stmt.table_name, "students")
        self.assertIsNotNone(stmt.where_clause)
        self.assertEqual(stmt.where_clause['column'], "id")
        self.assertEqual(stmt.where_clause['operator'], "=")
        self.assertEqual(stmt.where_clause['value'], 1)
    
    def test_delete_parsing(self):
        """Test DELETE statement parsing"""
        sql = "DELETE FROM students WHERE id = 1"
        stmt = self.parser.parse(sql)
        
        self.assertEqual(stmt.table_name, "students")
        self.assertEqual(stmt.where_clause['column'], "id")

class TestBTree(unittest.TestCase):
    """Test B+ tree implementation"""
    
    def setUp(self):
        self.btree = BTree(order=3)  # Small order for testing
    
    def test_insert_and_search(self):
        """Test basic insert and search operations"""
        self.btree.insert(1, "value1")
        self.btree.insert(2, "value2")
        self.btree.insert(3, "value3")
        
        self.assertEqual(self.btree.search(1), "value1")
        self.assertEqual(self.btree.search(2), "value2")
        self.assertEqual(self.btree.search(3), "value3")
        self.assertIsNone(self.btree.search(4))
    
    def test_split_behavior(self):
        """Test node splitting on overflow"""
        # Insert enough values to trigger splits
        for i in range(1, 10):
            self.btree.insert(i, f"value{i}")
        
        # Verify all values can still be found
        for i in range(1, 10):
            self.assertEqual(self.btree.search(i), f"value{i}")
    
    def test_range_query(self):
        """Test range query functionality"""
        for i in [3, 1, 4, 1, 5, 9, 2, 6]:
            self.btree.insert(i, f"value{i}")
        
        results = self.btree.range_query(2, 5)
        keys = [key for key, value in results]
        
        # Should return keys 2, 3, 4, 5 in sorted order
        expected_keys = [2, 3, 4, 5]
        self.assertEqual(sorted(keys), expected_keys)

class TestMandukyaDB(unittest.TestCase):
    """Test main MandukyaDB functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        self.db = MandukyaDB(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_create_table(self):
        """Test table creation"""
        result = self.db.execute("CREATE TABLE test (id INTEGER, name TEXT);")
        self.assertIn("created successfully", result)
        
        tables = self.db.get_tables()
        self.assertIn("test", tables)
    
    def test_insert_and_select(self):
        """Test insert and select operations"""
        # Create table
        self.db.execute("CREATE TABLE heroes (id INTEGER, name TEXT);")
        
        # Insert data
        row_id = self.db.execute("INSERT INTO heroes VALUES (1, 'Arjuna');")
        self.assertIsInstance(row_id, int)
        
        # Select data
        results = self.db.execute("SELECT * FROM heroes;")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (1, "Arjuna"))
    
    def test_where_clause(self):
        """Test WHERE clause functionality"""
        # Setup
        self.db.execute("CREATE TABLE numbers (id INTEGER, value INTEGER);")
        self.db.execute("INSERT INTO numbers VALUES (1, 10);")
        self.db.execute("INSERT INTO numbers VALUES (2, 20);")
        self.db.execute("INSERT INTO numbers VALUES (3, 30);")
        
        # Test equals
        results = self.db.execute("SELECT * FROM numbers WHERE value = 20;")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (2, 20))
        
        # Test greater than  
        results = self.db.execute("SELECT * FROM numbers WHERE value > 15;")
        self.assertEqual(len(results), 2)
    
    def test_delete(self):
        """Test delete operations"""
        # Setup
        self.db.execute("CREATE TABLE items (id INTEGER, name TEXT);")
        self.db.execute("INSERT INTO items VALUES (1, 'item1');")
        self.db.execute("INSERT INTO items VALUES (2, 'item2');")
        
        # Delete one item
        deleted = self.db.execute("DELETE FROM items WHERE id = 1;")
        self.assertEqual(deleted, 1)
        
        # Verify deletion
        results = self.db.execute("SELECT * FROM items;")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "item2")
    
    def test_python_api(self):
        """Test Python API methods"""
        # Create table using Python API
        self.db.create_table("users", [("id", "INTEGER"), ("email", "TEXT")])
        
        # Insert using Python API
        row_id = self.db.insert("users", [1, "test@example.com"])
        self.assertIsInstance(row_id, int)
        
        # Select using Python API
        results = self.db.select("users")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (1, "test@example.com"))
        
        # Select with WHERE using Python API
        results = self.db.select("users", where={"column": "id", "value": 1})
        self.assertEqual(len(results), 1)
    
    def test_caching(self):
        """Test query result caching"""
        # Setup
        self.db.execute("CREATE TABLE cache_test (id INTEGER, data TEXT);")
        self.db.execute("INSERT INTO cache_test VALUES (1, 'test');")
        
        # First query (cache miss)
        results1 = self.db.execute("SELECT * FROM cache_test;")
        
        # Second query (should be cache hit)
        results2 = self.db.execute("SELECT * FROM cache_test;")
        
        # Results should be identical
        self.assertEqual(results1, results2)
        
        # Check cache stats
        stats = self.db.get_stats()
        self.assertIn('cache_stats', stats)
    
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid SQL
        with self.assertRaises(MandukyaError):
            self.db.execute("INVALID SQL STATEMENT")
        
        # Test selecting from non-existent table
        with self.assertRaises(MandukyaError):
            self.db.execute("SELECT * FROM nonexistent;")
        
        # Test inserting into non-existent table
        with self.assertRaises(MandukyaError):
            self.db.execute("INSERT INTO nonexistent VALUES (1);")
    
    def test_context_manager(self):
        """Test context manager functionality"""
        with MandukyaDB(":memory:") as db:
            db.execute("CREATE TABLE temp (id INTEGER);")
            db.execute("INSERT INTO temp VALUES (1);")
            results = db.execute("SELECT * FROM temp;")
            self.assertEqual(results, [(1,)])
    
    def test_persistence(self):
        """Test data persistence across database reopens"""
        # Create and populate database
        db1 = MandukyaDB(self.db_path)
        db1.execute("CREATE TABLE persistent (id INTEGER, name TEXT);")
        db1.execute("INSERT INTO persistent VALUES (1, 'test');")
        db1.close()
        
        # Reopen database and verify data persists
        db2 = MandukyaDB(self.db_path)
        results = db2.execute("SELECT * FROM persistent;")
        self.assertEqual(results, [(1, "test")])
        db2.close()

class TestPerformance(unittest.TestCase):
    """Performance tests for MandukyaDB"""
    
    def setUp(self):
        self.db = MandukyaDB(":memory:")
        self.db.execute("CREATE TABLE perf_test (id INTEGER, value INTEGER);")
    
    def tearDown(self):
        self.db.close()
    
    def test_bulk_insert(self):
        """Test performance with bulk inserts"""
        import time
        
        start_time = time.time()
        
        # Insert 1000 rows
        for i in range(1000):
            self.db.execute(f"INSERT INTO perf_test VALUES ({i}, {i*2});")
        
        insert_time = time.time() - start_time
        
        # Verify all rows inserted
        results = self.db.execute("SELECT COUNT(*) FROM perf_test;")
        # Note: COUNT(*) not implemented, so check differently
        results = self.db.execute("SELECT * FROM perf_test;")
        self.assertEqual(len(results), 1000)
        
        print(f"\nBulk insert performance: {insert_time:.3f}s for 1000 rows")
    
    def test_cache_performance(self):
        """Test cache performance improvement"""
        import time
        
        # Insert test data
        for i in range(100):
            self.db.execute(f"INSERT INTO perf_test VALUES ({i}, {i});")
        
        query = "SELECT * FROM perf_test WHERE value > 50;"
        
        # First query (cache miss)
        start_time = time.time()
        results1 = self.db.execute(query)
        first_time = time.time() - start_time
        
        # Second query (cache hit)
        start_time = time.time()
        results2 = self.db.execute(query)
        second_time = time.time() - start_time
        
        self.assertEqual(results1, results2)
        print(f"\nCache performance: {first_time:.4f}s → {second_time:.4f}s")
        
        if first_time > 0:
            improvement = (first_time - second_time) / first_time * 100
            print(f"Performance improvement: {improvement:.1f}%")

def run_tests():
    """Run all test suites"""
    print("🧪 Running MandukyaDB Test Suite")
    print("=" * 40)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSQLParser))
    suite.addTests(loader.loadTestsFromTestCase(TestBTree))
    suite.addTests(loader.loadTestsFromTestCase(TestMandukyaDB))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*40}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
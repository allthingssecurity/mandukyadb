#!/usr/bin/env python3
"""
MandukyaDB Example - Demonstrates the four states of consciousness in action
"""

import sys
import os
import time

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.mandukya_db import MandukyaDB
from src.exceptions import MandukyaError

def demo_basic_operations():
    """Demo basic SQL operations"""
    print("=== MandukyaDB Basic Operations Demo ===")
    
    # Create database
    with MandukyaDB("example.db") as db:
        print(f"Created database: {db}")
        
        # Create table
        print("\n1. Creating 'students' table...")
        result = db.execute("CREATE TABLE students (id INTEGER, name TEXT);")
        print(f"Result: {result}")
        
        # Insert data
        print("\n2. Inserting students...")
        db.execute("INSERT INTO students VALUES (1, 'Arjuna');")
        db.execute("INSERT INTO students VALUES (2, 'Krishna');")
        db.execute("INSERT INTO students VALUES (3, 'Bhima');")
        print("Inserted 3 students")
        
        # Select all
        print("\n3. Selecting all students...")
        results = db.execute("SELECT * FROM students;")
        for row in results:
            print(f"  {row}")
        
        # Select with WHERE clause
        print("\n4. Selecting student with id=2...")
        results = db.execute("SELECT * FROM students WHERE id = 2;")
        for row in results:
            print(f"  {row}")
        
        # Delete a row
        print("\n5. Deleting student with id=3...")
        deleted = db.execute("DELETE FROM students WHERE id = 3;")
        print(f"Deleted {deleted} row(s)")
        
        # Verify deletion
        print("\n6. Final student list...")
        results = db.execute("SELECT * FROM students;")
        for row in results:
            print(f"  {row}")

def demo_python_api():
    """Demo Pythonic API"""
    print("\n\n=== MandukyaDB Python API Demo ===")
    
    with MandukyaDB("api_demo.db") as db:
        # Create table using Python API
        print("\n1. Creating 'heroes' table using Python API...")
        db.create_table("heroes", [
            ("id", "INTEGER"),
            ("name", "TEXT"),
            ("weapon", "TEXT"),
            ("strength", "INTEGER")
        ])
        
        # Insert using Python API
        print("\n2. Inserting heroes using Python API...")
        db.insert("heroes", [1, "Arjuna", "Gandiva", 95])
        db.insert("heroes", [2, "Bhima", "Mace", 100])
        db.insert("heroes", [3, "Karna", "Vijaya", 98])
        
        # Select using Python API
        print("\n3. Selecting all heroes...")
        results = db.select("heroes")
        for row in results:
            print(f"  {row}")
        
        # Select with WHERE clause
        print("\n4. Selecting heroes with strength > 96...")
        results = db.select("heroes", where={
            "column": "strength",
            "operator": ">", 
            "value": 96
        })
        for row in results:
            print(f"  {row}")

def demo_cache_performance():
    """Demo caching performance"""
    print("\n\n=== MandukyaDB Cache Performance Demo ===")
    
    with MandukyaDB("perf_demo.db") as db:
        # Create table with more data
        db.execute("CREATE TABLE numbers (id INTEGER, value INTEGER);")
        
        print("\n1. Inserting 100 numbers...")
        for i in range(1, 101):
            db.insert("numbers", [i, i * i])
        
        # First query (cache miss)
        print("\n2. First query (cache miss)...")
        start_time = time.time()
        results = db.execute("SELECT * FROM numbers WHERE value > 5000;")
        first_time = time.time() - start_time
        print(f"Found {len(results)} rows in {first_time:.4f} seconds")
        
        # Second query (cache hit)
        print("\n3. Second query (cache hit)...")
        start_time = time.time()
        results = db.execute("SELECT * FROM numbers WHERE value > 5000;")
        second_time = time.time() - start_time
        print(f"Found {len(results)} rows in {second_time:.4f} seconds")
        
        # Show performance improvement
        if first_time > 0:
            improvement = (first_time - second_time) / first_time * 100
            print(f"Cache improved performance by {improvement:.1f}%")
        
        # Show statistics
        print("\n4. Database statistics...")
        stats = db.get_stats()
        print(f"Execution stats: {stats['execution_stats']}")
        print(f"Cache stats: {stats['cache_stats']}")

def demo_philosophical_states():
    """Demo the four states of consciousness"""
    print("\n\n=== The Four States of Consciousness Demo ===")
    
    with MandukyaDB("philosophy.db") as db:
        print("\n🌅 Jagrat (Waking State) - Storage Layer")
        print("Creating persistent table structure...")
        db.execute("CREATE TABLE consciousness (state TEXT, description TEXT);")
        
        print("\n💭 Swapna (Dreaming State) - Query Planning")
        print("Parsing and planning INSERT operations...")
        db.execute("INSERT INTO consciousness VALUES ('Jagrat', 'Waking state - persistent storage');")
        db.execute("INSERT INTO consciousness VALUES ('Swapna', 'Dreaming state - query planning');")
        db.execute("INSERT INTO consciousness VALUES ('Sushupti', 'Deep sleep - memory cache');")
        db.execute("INSERT INTO consciousness VALUES ('Turiya', 'Pure consciousness - execution');")
        
        print("\n😴 Sushupti (Deep Sleep State) - Memory Cache")
        print("First query loads data into memory cache...")
        results1 = db.execute("SELECT * FROM consciousness;")
        
        print("\n✨ Turiya (Pure Consciousness) - Execution Engine")
        print("Second query uses cached results for instant access...")
        results2 = db.execute("SELECT * FROM consciousness;")
        
        print("\nThe four states working in harmony:")
        for row in results2:
            print(f"  {row[0]}: {row[1]}")

def main():
    """Run all demos"""
    print("🕉️  MandukyaDB - Inspired by the Mandūkya Upaniṣad")
    print("=" * 50)
    
    try:
        demo_basic_operations()
        demo_python_api()
        demo_cache_performance()
        demo_philosophical_states()
        
        print("\n\n✅ All demos completed successfully!")
        print("\nMandukyaDB demonstrates the integration of:")
        print("  • Jagrat (Storage) - Persistent B+ tree data structures")
        print("  • Swapna (Planning) - SQL parsing and query optimization") 
        print("  • Sushupti (Cache) - In-memory caching and indexing")
        print("  • Turiya (Execution) - Unified query execution engine")
        
    except MandukyaError as e:
        print(f"❌ MandukyaDB Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    finally:
        # Cleanup demo files
        for filename in ["example.db", "api_demo.db", "perf_demo.db", "philosophy.db"]:
            if os.path.exists(filename):
                os.remove(filename)
        print("\n🧹 Cleaned up demo database files")

if __name__ == "__main__":
    main()
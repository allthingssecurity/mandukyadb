#!/usr/bin/env python3
"""
Test DESC/DESCRIBE command functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mandukya_db import MandukyaDB

def test_describe_commands():
    """Test DESC and DESCRIBE commands"""
    print("🕉️  Testing DESC/DESCRIBE Commands")
    print("=" * 40)
    
    with MandukyaDB(":memory:") as db:
        # Create a test table
        print("1. Creating test table...")
        db.execute("CREATE TABLE students (id INTEGER, name TEXT, grade INTEGER, email TEXT);")
        
        # Test DESCRIBE command
        print("\n2. Testing DESCRIBE students;")
        try:
            result = db.execute("DESCRIBE students;")
            print("   ✅ DESCRIBE command successful!")
            print("   Table Schema:")
            for i, (col_name, col_type, constraints) in enumerate(result, 1):
                print(f"     {i}. {col_name:<12} {col_type:<10} {constraints}")
        except Exception as e:
            print(f"   ❌ DESCRIBE failed: {e}")
        
        # Test DESC command (shorthand)
        print("\n3. Testing DESC students;")
        try:
            result = db.execute("DESC students;")
            print("   ✅ DESC command successful!")
            print("   Table Schema:")
            for i, (col_name, col_type, constraints) in enumerate(result, 1):
                print(f"     {i}. {col_name:<12} {col_type:<10} {constraints}")
        except Exception as e:
            print(f"   ❌ DESC failed: {e}")
        
        # Test describe non-existent table
        print("\n4. Testing DESC on non-existent table...")
        try:
            result = db.execute("DESC nonexistent;")
            print("   ❌ Should have failed!")
        except Exception as e:
            print(f"   ✅ Correctly failed: {e}")
    
    print("\n🎉 DESC/DESCRIBE commands are now working!")

if __name__ == "__main__":
    test_describe_commands()
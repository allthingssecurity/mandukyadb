#!/usr/bin/env python3
"""
MandukyaDB Interactive Test - Simulates CLI commands
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mandukya_db import MandukyaDB

def test_interactive_session():
    """Simulate an interactive CLI session"""
    
    print("🕉️  MandukyaDB Interactive Test Session")
    print("=" * 50)
    print("Simulating CLI commands you can try...")
    print()
    
    # Create database connection
    db = MandukyaDB("test_database.db")
    print("✅ Connected to database: test_database.db")
    print()
    
    commands = [
        # DDL Commands
        ("CREATE TABLE employees (id INTEGER, name TEXT, department TEXT, salary INTEGER);", "Create employees table"),
        ("CREATE TABLE projects (proj_id INTEGER, name TEXT, budget INTEGER);", "Create projects table"),
        
        # Show schema
        (".tables", "List all tables"),
        (".schema", "Show database schema"),
        
        # DML Commands - Insert data
        ("INSERT INTO employees VALUES (1, 'Arjuna', 'Engineering', 95000);", "Insert employee 1"),
        ("INSERT INTO employees VALUES (2, 'Krishna', 'Management', 120000);", "Insert employee 2"), 
        ("INSERT INTO employees VALUES (3, 'Bhima', 'Sales', 75000);", "Insert employee 3"),
        ("INSERT INTO employees VALUES (4, 'Draupadi', 'HR', 85000);", "Insert employee 4"),
        
        ("INSERT INTO projects VALUES (1, 'Database Project', 500000);", "Insert project 1"),
        ("INSERT INTO projects VALUES (2, 'Web App', 300000);", "Insert project 2"),
        
        # Query data
        ("SELECT * FROM employees;", "Select all employees"),
        ("SELECT name, salary FROM employees WHERE salary > 80000;", "High-salary employees"),
        ("SELECT department FROM employees WHERE name = 'Krishna';", "Krishna's department"),
        ("SELECT * FROM projects WHERE budget > 400000;", "Large projects"),
        
        # Statistics and info
        (".stats", "Database statistics"),
        (".sample employees", "Sample employee data"),
        
        # Delete operation
        ("DELETE FROM employees WHERE salary < 80000;", "Delete low-salary employees"),
        ("SELECT * FROM employees;", "Verify deletion"),
    ]
    
    for i, (command, description) in enumerate(commands, 1):
        print(f"{i:2d}. {description}")
        print(f"    Command: {command}")
        
        try:
            if command.startswith('.'):
                # Handle CLI commands
                if command == '.tables':
                    tables = db.get_tables()
                    if tables:
                        print(f"    Result: Tables: {', '.join(tables)}")
                    else:
                        print(f"    Result: No tables found")
                        
                elif command == '.schema':
                    tables = db.get_tables()
                    print(f"    Result: Database has {len(tables)} tables")
                    for table_name in tables:
                        table = db.engine.storage.get_table(table_name)
                        if table:
                            cols = [f"{col.name}({col.data_type})" for col in table.columns]
                            print(f"            {table_name}: {', '.join(cols)}")
                            
                elif command == '.stats':
                    stats = db.get_stats()
                    exec_stats = stats['execution_stats']
                    cache_stats = stats['cache_stats']
                    print(f"    Result: Queries: {exec_stats['queries_executed']}, Cache: {cache_stats['hit_rate']}")
                    
                elif command.startswith('.sample'):
                    table_name = command.split()[1]
                    results = db.execute(f"SELECT * FROM {table_name}")
                    print(f"    Result: {len(results)} rows in {table_name}")
                    for row in results[:3]:  # Show first 3 rows
                        print(f"            {row}")
                        
            else:
                # Handle SQL commands
                result = db.execute(command)
                
                if isinstance(result, list):
                    print(f"    Result: {len(result)} rows returned")
                    if len(result) <= 5:  # Show all if 5 or fewer
                        for row in result:
                            print(f"            {row}")
                    else:  # Show first 3 and last 1
                        for row in result[:3]:
                            print(f"            {row}")
                        print(f"            ... ({len(result)-4} more rows)")
                        print(f"            {result[-1]}")
                elif isinstance(result, int):
                    if 'INSERT' in command:
                        print(f"    Result: Inserted row with ID: {result}")
                    elif 'DELETE' in command:
                        print(f"    Result: Deleted {result} row(s)")
                else:
                    print(f"    Result: {result}")
                    
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        print()
    
    # Show final statistics
    print("📊 Final Database Statistics:")
    stats = db.get_stats()
    print(f"   • Total queries executed: {stats['execution_stats']['queries_executed']}")
    print(f"   • Cache hit rate: {stats['cache_stats']['hit_rate']}")
    print(f"   • Tables created: {len(stats['tables'])}")
    print(f"   • Tables: {', '.join(stats['tables'])}")
    
    db.close()
    print("\n✅ Test session completed successfully!")
    
    print("\n🎯 How to use the actual CLI:")
    print("   1. Run: python3 mandukya_cli.py your_database.db")
    print("   2. Type SQL commands ending with semicolon (;)")
    print("   3. Use .help for CLI commands")
    print("   4. Use .exit to quit")

if __name__ == "__main__":
    test_interactive_session()
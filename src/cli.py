#!/usr/bin/env python3
"""
MandukyaDB CLI - Interactive database shell
"""

import sys
import os
import cmd
import readline

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.mandukya_db import MandukyaDB
from src.exceptions import MandukyaError

class MandukyaCLI(cmd.Cmd):
    """Interactive CLI for MandukyaDB"""
    
    intro = """
🕉️  MandukyaDB Interactive Shell
Inspired by the Mandūkya Upaniṣad - Four States of Consciousness

Commands:
  .help       - Show this help
  .tutorial   - Interactive tutorial
  .tables     - List all tables  
  .schema     - Show all table schemas
  .describe   - Describe table structure
  .sample     - Show sample data from table
  .stats      - Show database statistics
  .cache      - Show cache statistics
  .clear      - Clear screen
  .exit       - Exit the shell
  
Enter SQL statements ending with semicolon (;)
Example: CREATE TABLE students (id INTEGER, name TEXT);
"""
    
    prompt = "mandukya> "
    
    def __init__(self, database_path=None):
        super().__init__()
        self.database_path = database_path or ":memory:"
        self.db = None
        self.multiline_buffer = ""
        
    def preloop(self):
        """Initialize database connection"""
        try:
            self.db = MandukyaDB(self.database_path)
            print(f"Connected to database: {self.database_path}")
            print(f"Database object: {self.db}")
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            return False
    
    def postloop(self):
        """Clean up database connection"""
        if self.db:
            self.db.close()
            print("\nDatabase connection closed.")
    
    def default(self, line):
        """Handle SQL statements"""
        if not line.strip():
            return
        
        # Handle multi-line SQL statements
        self.multiline_buffer += line + " "
        
        # Check if statement is complete (ends with semicolon)
        if line.strip().endswith(';'):
            sql = self.multiline_buffer.strip()
            self.multiline_buffer = ""
            self._execute_sql(sql)
        else:
            # Continue multi-line input
            self.prompt = "     ... "
    
    def _execute_sql(self, sql):
        """Execute SQL statement and display results"""
        self.prompt = "mandukya> "  # Reset prompt
        
        try:
            start_time = __import__('time').time()
            result = self.db.execute(sql)
            end_time = __import__('time').time()
            
            # Display results based on statement type
            if isinstance(result, list):
                # SELECT results
                if result:
                    print(f"\n{len(result)} row(s) returned:")
                    for i, row in enumerate(result, 1):
                        print(f"  {i}: {row}")
                else:
                    print("\n0 rows returned.")
            elif isinstance(result, int):
                # INSERT/DELETE row count
                if 'INSERT' in sql.upper():
                    print(f"\nInserted row with ID: {result}")
                elif 'DELETE' in sql.upper():
                    print(f"\nDeleted {result} row(s)")
            else:
                # CREATE TABLE or other messages
                print(f"\n{result}")
            
            # Show execution time
            print(f"Execution time: {(end_time - start_time) * 1000:.2f}ms")
            
        except MandukyaError as e:
            print(f"\nError: {e}")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
    
    def do_help(self, arg):
        """Show help information"""
        print(self.intro)
        
        print("\nSupported SQL Statements:")
        print("  CREATE TABLE table_name (column_name type, ...);")
        print("  INSERT INTO table_name VALUES (value1, value2, ...);")
        print("  SELECT [columns|*] FROM table_name [WHERE condition];")
        print("  DELETE FROM table_name [WHERE condition];")
        
        print("\nExamples:")
        print("  CREATE TABLE heroes (id INTEGER, name TEXT, strength INTEGER);")
        print("  INSERT INTO heroes VALUES (1, 'Arjuna', 95);")
        print("  SELECT * FROM heroes;")
        print("  SELECT name FROM heroes WHERE strength > 90;")
        print("  DELETE FROM heroes WHERE id = 1;")
    
    def do_tables(self, arg):
        """List all tables"""
        try:
            tables = self.db.get_tables()
            if tables:
                print(f"\nTables in database:")
                for table in tables:
                    print(f"  {table}")
            else:
                print("\nNo tables in database.")
        except Exception as e:
            print(f"Error listing tables: {e}")
    
    def do_stats(self, arg):
        """Show database statistics"""
        try:
            stats = self.db.get_stats()
            print(f"\n📊 Database Statistics:")
            print(f"  Tables: {len(stats.get('tables', []))}")
            
            exec_stats = stats.get('execution_stats', {})
            print(f"  Queries executed: {exec_stats.get('queries_executed', 0)}")
            print(f"  Cache hits: {exec_stats.get('cache_hits', 0)}")
            print(f"  Cache misses: {exec_stats.get('cache_misses', 0)}")
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
    
    def do_cache(self, arg):
        """Show cache statistics"""
        try:
            stats = self.db.get_stats()
            cache_stats = stats.get('cache_stats', {})
            
            print(f"\n💾 Cache Statistics:")
            print(f"  Hit rate: {cache_stats.get('hit_rate', 'N/A')}")
            print(f"  Query cache size: {cache_stats.get('query_cache_size', 0)}")
            print(f"  Table cache size: {cache_stats.get('table_cache_size', 0)}")
            
        except Exception as e:
            print(f"Error getting cache statistics: {e}")
    
    def do_exit(self, arg):
        """Exit the CLI"""
        print("\nExiting MandukyaDB CLI...")
        return True
    
    def do_quit(self, arg):
        """Exit the CLI (alias for exit)"""
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        print()  # New line for clean exit
        return self.do_exit(arg)
    
    def emptyline(self):
        """Handle empty lines"""
        pass

    def do_describe(self, table_name):
        """Describe table structure: .describe table_name"""
        if not table_name.strip():
            print("Usage: .describe <table_name>")
            return
        
        try:
            # Try to get table metadata from storage
            table = self.db.engine.storage.get_table(table_name.strip())
            if table:
                print(f"\nTable: {table.name}")
                print("Columns:")
                for col in table.columns:
                    constraints = " ".join(col.constraints) if col.constraints else ""
                    print(f"  {col.name:<15} {col.data_type:<10} {constraints}")
            else:
                print(f"\nTable '{table_name}' does not exist.")
        except Exception as e:
            print(f"Error describing table: {e}")
    
    def do_schema(self, arg):
        """Show all tables and their schemas"""
        try:
            tables = self.db.get_tables()
            if not tables:
                print("\nNo tables in database.")
                return
            
            print(f"\n📋 Database Schema:")
            for table_name in tables:
                table = self.db.engine.storage.get_table(table_name)
                if table:
                    print(f"\n  Table: {table_name}")
                    for col in table.columns:
                        constraints = " ".join(col.constraints) if col.constraints else ""
                        print(f"    {col.name:<15} {col.data_type:<10} {constraints}")
        except Exception as e:
            print(f"Error showing schema: {e}")
    
    def do_sample(self, table_name):
        """Show sample data from table: .sample table_name"""
        if not table_name.strip():
            print("Usage: .sample <table_name>")
            return
        
        try:
            sql = f"SELECT * FROM {table_name.strip()}"
            result = self.db.execute(sql)
            
            if result:
                print(f"\nSample data from '{table_name}' (showing up to 5 rows):")
                for i, row in enumerate(result[:5], 1):
                    print(f"  {i}: {row}")
                if len(result) > 5:
                    print(f"  ... and {len(result) - 5} more rows")
            else:
                print(f"\nNo data in table '{table_name}'")
                
        except Exception as e:
            print(f"Error sampling table: {e}")
    
    def do_clear(self, arg):
        """Clear the screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def do_tutorial(self, arg):
        """Show interactive tutorial"""
        print("""
🎓 MandukyaDB Interactive Tutorial
===============================

Let's create a simple database step by step:

1. Create a students table:
   CREATE TABLE students (id INTEGER, name TEXT, grade INTEGER);

2. Insert some data:
   INSERT INTO students VALUES (1, 'Arjuna', 95);
   INSERT INTO students VALUES (2, 'Krishna', 98);
   INSERT INTO students VALUES (3, 'Bhima', 87);

3. Query the data:
   SELECT * FROM students;
   SELECT name FROM students WHERE grade > 90;

4. Use CLI commands:
   .tables          - List all tables
   .describe students - Show table structure
   .sample students   - Show sample data
   .stats           - Database statistics

5. Clean up:
   DELETE FROM students WHERE grade < 90;

Try these commands now!
        """)

def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MandukyaDB Interactive CLI")
    parser.add_argument("database", nargs="?", default=":memory:", 
                       help="Database file path (default: in-memory)")
    parser.add_argument("--version", action="version", version="MandukyaDB 1.0.0")
    
    args = parser.parse_args()
    
    try:
        cli = MandukyaCLI(args.database)
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"CLI error: {e}")

if __name__ == "__main__":
    main()
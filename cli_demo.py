#!/usr/bin/env python3
"""
MandukyaDB CLI Demo - Shows typical interactive usage
This script demonstrates what you would type in the interactive CLI
"""

print("""
🕉️  MandukyaDB Interactive CLI Demonstration
============================================

Here's a typical workflow using the MandukyaDB interactive shell:

1. START THE CLI:
   $ python3 mandukya_cli.py mycompany.db

2. GET HELP AND TUTORIAL:
   mandukya> .help
   mandukya> .tutorial

3. CREATE DATABASE SCHEMA (DDL):

   # Create employees table
   mandukya> CREATE TABLE employees (
        ...      id INTEGER,
        ...      name TEXT,
        ...      department TEXT,
        ...      salary INTEGER,
        ...      hire_date TEXT
        ...  );

   # Create departments table  
   mandukya> CREATE TABLE departments (
        ...      dept_id INTEGER,
        ...      dept_name TEXT,
        ...      manager TEXT
        ...  );

4. VIEW SCHEMA:
   mandukya> .tables
   mandukya> .schema
   mandukya> .describe employees

5. INSERT DATA (DML):

   # Insert employees
   mandukya> INSERT INTO employees VALUES (1, 'Arjuna', 'Engineering', 95000, '2024-01-15');
   mandukya> INSERT INTO employees VALUES (2, 'Krishna', 'Management', 120000, '2024-01-01');
   mandukya> INSERT INTO employees VALUES (3, 'Bhima', 'Sales', 75000, '2024-02-01');
   mandukya> INSERT INTO employees VALUES (4, 'Draupadi', 'HR', 85000, '2024-01-20');

   # Insert departments
   mandukya> INSERT INTO departments VALUES (1, 'Engineering', 'Arjuna');
   mandukya> INSERT INTO departments VALUES (2, 'Management', 'Krishna');
   mandukya> INSERT INTO departments VALUES (3, 'Sales', 'Bhima');

6. QUERY DATA:

   # Select all employees
   mandukya> SELECT * FROM employees;

   # Filter by department
   mandukya> SELECT name, salary FROM employees WHERE department = 'Engineering';

   # Filter by salary
   mandukya> SELECT name, department FROM employees WHERE salary > 80000;

   # View sample data
   mandukya> .sample employees
   mandukya> .sample departments

7. UPDATE AND DELETE (DML):

   # Delete low performers (if we had UPDATE, we'd use that)
   mandukya> DELETE FROM employees WHERE salary < 80000;

   # Verify deletion
   mandukya> SELECT * FROM employees;

8. DATABASE STATISTICS:
   mandukya> .stats
   mandukya> .cache

9. EXIT:
   mandukya> .exit

EXPECTED OUTPUT EXAMPLES:
========================

After CREATE TABLE:
   Table 'employees' created successfully
   Execution time: 2.34ms

After INSERT:
   Inserted row with ID: 1
   Execution time: 1.12ms

After SELECT * FROM employees:
   4 row(s) returned:
     1: (1, 'Arjuna', 'Engineering', 95000, '2024-01-15')
     2: (2, 'Krishna', 'Management', 120000, '2024-01-01')  
     3: (3, 'Bhima', 'Sales', 75000, '2024-02-01')
     4: (4, 'Draupadi', 'HR', 85000, '2024-01-20')

After .schema:
   📋 Database Schema:
   
     Table: employees
       id              INTEGER    
       name            TEXT       
       department      TEXT       
       salary          INTEGER    
       hire_date       TEXT

     Table: departments  
       dept_id         INTEGER    
       dept_name       TEXT       
       manager         TEXT

After .stats:
   📊 Database Statistics:
     Tables: 2
     Queries executed: 12
     Cache hits: 3
     Cache misses: 5

KEY FEATURES DEMONSTRATED:
=========================

✅ DDL Operations:
   - CREATE TABLE with multiple columns and data types
   - Schema inspection with .tables, .schema, .describe

✅ DML Operations:  
   - INSERT INTO with various data types
   - SELECT with * and specific columns
   - WHERE clauses with different operators
   - DELETE with conditions

✅ Interactive Features:
   - Multi-line SQL support (notice the ... prompt)
   - Command completion and history
   - Built-in help and tutorial
   - Performance timing for each query

✅ Database Management:
   - Persistent file-based storage
   - Caching statistics and performance metrics
   - Sample data viewing
   - Error handling with helpful messages

✅ The Four States in Action:
   - Jagrat (Storage): Data persisted to mycompany.db file
   - Swapna (Planning): SQL parsing and query optimization
   - Sushupti (Cache): Query result caching for performance  
   - Turiya (Execution): Unified execution with timing metrics

Try these commands in your CLI session!
""")

if __name__ == "__main__":
    print("Copy and paste the commands above into your MandukyaDB CLI session.")
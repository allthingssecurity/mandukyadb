# ANSI SQL Compliance - MandukyaDB

MandukyaDB aims for ANSI SQL compliance while maintaining simplicity and performance. This document outlines current compliance status and future enhancements.

## Supported SQL Features

### Data Definition Language (DDL)

#### CREATE TABLE
- ✅ Basic table creation with column definitions
- ✅ Supported data types: INTEGER, TEXT, REAL, BLOB
- ⚠️  Limited constraint support (PRIMARY KEY, NOT NULL planned)

```sql
CREATE TABLE students (
    id INTEGER,
    name TEXT,
    grade REAL
);
```

#### DROP TABLE
- ❌ Not yet implemented (planned for v1.1)

### Data Manipulation Language (DML)

#### INSERT
- ✅ INSERT INTO table VALUES (...)
- ❌ INSERT INTO table (columns) VALUES (...) - planned
- ❌ INSERT INTO table SELECT ... - planned

```sql
INSERT INTO students VALUES (1, 'Arjuna', 95.5);
```

#### SELECT
- ✅ SELECT * FROM table
- ✅ SELECT column1, column2 FROM table  
- ✅ WHERE clause with basic operators (=, !=, <, <=, >, >=)
- ❌ JOIN operations - planned for v1.2
- ❌ GROUP BY, HAVING - planned for v1.2
- ❌ ORDER BY, LIMIT - partially parsed, execution planned
- ❌ Subqueries - planned for v1.3

```sql
SELECT name, grade FROM students WHERE grade > 90;
```

#### DELETE
- ✅ DELETE FROM table WHERE condition
- ✅ DELETE FROM table (all rows)

```sql
DELETE FROM students WHERE grade < 60;
```

#### UPDATE
- ❌ Not yet implemented (planned for v1.1)

### Data Query Language (DQL)

#### Operators
- ✅ Comparison: =, !=, <, <=, >, >=
- ❌ LIKE, IN, BETWEEN - planned for v1.1
- ❌ AND, OR in WHERE clauses - planned for v1.1

#### Functions
- ❌ Aggregate functions (COUNT, SUM, AVG, etc.) - planned for v1.2
- ❌ String functions (UPPER, LOWER, SUBSTR, etc.) - planned for v1.2
- ❌ Math functions (ABS, ROUND, etc.) - planned for v1.2

## Data Types

### Supported Types
- **INTEGER**: 64-bit signed integers
- **TEXT**: Variable-length strings
- **REAL**: Double-precision floating point
- **BLOB**: Binary data (basic support)

### ANSI SQL Type Mapping
| ANSI SQL Type | MandukyaDB Type | Status |
|---------------|-----------------|--------|
| INTEGER       | INTEGER         | ✅      |
| VARCHAR(n)    | TEXT            | ✅      |
| CHAR(n)       | TEXT            | ✅      |
| DECIMAL(p,s)  | REAL            | ⚠️      |
| FLOAT         | REAL            | ✅      |
| DOUBLE        | REAL            | ✅      |
| DATE          | TEXT            | ⚠️      |
| TIME          | TEXT            | ⚠️      |
| TIMESTAMP     | TEXT            | ⚠️      |
| BOOLEAN       | INTEGER         | ⚠️      |

## Transactions

- ❌ BEGIN TRANSACTION - planned for v1.1
- ❌ COMMIT - basic auto-commit implemented
- ❌ ROLLBACK - planned for v1.1
- ❌ SAVEPOINT - planned for v1.2

## Constraints

- ❌ PRIMARY KEY - planned for v1.1
- ❌ FOREIGN KEY - planned for v1.2  
- ❌ UNIQUE - planned for v1.1
- ❌ NOT NULL - planned for v1.1
- ❌ CHECK - planned for v1.2
- ❌ DEFAULT - planned for v1.1

## Indexes

- ✅ Automatic B+ tree indexes on all columns
- ❌ CREATE INDEX - planned for v1.1
- ❌ DROP INDEX - planned for v1.1
- ❌ Composite indexes - planned for v1.2

## Schema Information

- ❌ INFORMATION_SCHEMA - planned for v1.2
- ❌ System tables - planned for v1.1

## Compliance Roadmap

### Version 1.1 (Near Term)
- UPDATE statements
- DROP TABLE
- Basic constraints (NOT NULL, PRIMARY KEY, UNIQUE)
- Explicit transactions (BEGIN, COMMIT, ROLLBACK)
- LIKE operator
- AND/OR in WHERE clauses

### Version 1.2 (Medium Term)  
- JOIN operations (INNER, LEFT, RIGHT)
- GROUP BY and HAVING
- ORDER BY and LIMIT execution
- Aggregate functions
- FOREIGN KEY constraints
- CREATE/DROP INDEX

### Version 1.3 (Long Term)
- Subqueries
- Views (CREATE VIEW)
- Advanced functions
- Window functions
- Common Table Expressions (WITH)

## Performance Characteristics

MandukyaDB optimizes for:
- **Fast reads** through B+ tree indexes and caching
- **Small footprint** with minimal dependencies
- **ACID properties** through write-ahead logging (planned)

## Deviations from ANSI SQL

1. **Simplified parser**: Does not support all SQL syntax variations
2. **Limited data types**: Focus on core types for simplicity
3. **No NULL handling**: NULL values not yet fully implemented
4. **Case sensitivity**: Currently case-sensitive for identifiers
5. **String literals**: Only single-quote strings supported

## Testing Compliance

MandukyaDB includes a comprehensive test suite to verify SQL compliance:

```bash
python tests/test_mandukyadb.py
```

The test suite covers:
- SQL parsing accuracy
- Query execution correctness  
- Data persistence
- Performance benchmarks
- Error handling

## Philosophy Integration

The four states of consciousness are reflected in SQL compliance:

- **Jagrat (Storage)**: ACID compliance through persistent B+ trees
- **Swapna (Planning)**: SQL parsing and query optimization
- **Sushupti (Memory)**: Caching for performance
- **Turiya (Execution)**: Unified query execution with correct results

This ensures that while MandukyaDB may not support every ANSI SQL feature immediately, the features it does support work correctly and efficiently, following the philosophical principles of the Mandūkya Upaniṣad.
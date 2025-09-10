# MandukyaDB

A lightweight, embeddable relational database inspired by the Mandūkya Upaniṣad.

## Philosophy

MandukyaDB follows the four states of consciousness from the Mandūkya Upaniṣad:

- **Jagrat (Waking)** - Storage Layer: Persistent data written to disk
- **Swapna (Dreaming)** - Query Planner: Abstract query optimization 
- **Sushupti (Deep Sleep)** - Memory Cache: Fast in-memory operations
- **Turiya (Pure Consciousness)** - Execution Engine: Final query results

## Features

- ANSI SQL compliant
- Single-file database (like SQLite)
- No external dependencies
- B+ tree storage engine
- ACID transactions
- In-memory caching
- Python API and CLI

## Quick Start

```python
from mandukyadb import MandukyaDB

# Create database
db = MandukyaDB("example.db")

# Create table
db.execute("CREATE TABLE students (id INTEGER, name TEXT);")

# Insert data
db.execute("INSERT INTO students VALUES (1, 'Arjuna');")
db.execute("INSERT INTO students VALUES (2, 'Krishna');")

# Query data
results = db.execute("SELECT * FROM students;")
print(results)  # [(1, 'Arjuna'), (2, 'Krishna')]
```

## Installation

```bash
pip install mandukyadb
```

Or run locally:
```bash
python -m mandukyadb example.db
```

## Architecture

```
┌─────────────────┐
│  Turiya         │  Execution Engine
├─────────────────┤
│  Sushupti       │  Memory Cache  
├─────────────────┤
│  Swapna         │  Query Planner
├─────────────────┤
│  Jagrat         │  Storage Layer
└─────────────────┘
```
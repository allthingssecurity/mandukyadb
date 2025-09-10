#!/usr/bin/env python3
"""
Generate example outputs for the Remotion video by executing MandukyaDB
and writing a JSON file consumed by the video.
"""
import json
import os
import sys
import time

# Ensure src on path when run from repo root
ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from src.mandukya_db import MandukyaDB  # type: ignore

def step(title, sql=None, fn=None):
    started = time.time()
    result = None
    if fn is not None:
        result = fn()
    elapsed_ms = (time.time() - started) * 1000.0
    return {
        'title': title,
        'kind': infer_kind(sql, fn),
        'sql': sql,
        'result': result,
        'elapsed_ms': elapsed_ms,
    }

def infer_kind(sql, fn):
    if sql is None:
        return 'info'
    s = sql.strip().upper()
    if s.startswith('CREATE'):
        return 'create'
    if s.startswith('INSERT'):
        return 'insert'
    if s.startswith('SELECT'):
        return 'select'
    if s.startswith('DELETE'):
        return 'delete'
    return 'sql'

def main():
    steps = []
    with MandukyaDB(":memory:") as db:
        # Create table
        sql1 = "CREATE TABLE heroes (id INTEGER, name TEXT, strength INTEGER);"
        def do1():
            return db.execute(sql1)
        steps.append(step("Create table", sql1, do1))

        # Insert rows
        sql2 = """
        INSERT INTO heroes VALUES (1, 'Arjuna', 95);
        INSERT INTO heroes VALUES (2, 'Krishna', 98);
        INSERT INTO heroes VALUES (3, 'Bhima', 87);
        """.strip()
        def do2():
            # Execute sequentially to capture realistic behavior
            r = []
            for s in sql2.split(';'):
                s = s.strip()
                if not s:
                    continue
                r.append(db.execute(s+';'))
            return f"Inserted {len(r)} rows"
        steps.append(step("Insert rows", sql2, do2))

        # Select all
        sql3 = "SELECT * FROM heroes;"
        def do3():
            return db.execute(sql3)
        steps.append(step("Select all", sql3, do3))

        # Filtered select
        sql4 = "SELECT name FROM heroes WHERE strength > 90;"
        def do4():
            return db.execute(sql4)
        steps.append(step("Filter strong heroes", sql4, do4))

        # Delete one
        sql5 = "DELETE FROM heroes WHERE id = 1;"
        def do5():
            return f"Deleted {db.execute(sql5)} row"
        steps.append(step("Delete one", sql5, do5))

        # Stats (via API)
        def do6():
            return db.get_stats()
        steps.append({'title': 'Stats', 'kind': 'stats', 'sql': '(db.get_stats())', 'result': do6(), 'elapsed_ms': 0})

    out_dir = os.path.join(REPO, 'remotion', 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'examples.json')
    with open(out_file, 'w') as f:
        json.dump({'steps': steps}, f, indent=2)
    print(f"Wrote examples to {out_file}")

if __name__ == '__main__':
    main()

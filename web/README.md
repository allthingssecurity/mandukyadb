# MandukyaDB WASM Shell (Pyodide)

Run MandukyaDB entirely in the browser using Python→WASM (Pyodide). Type SQL and see results instantly.

## Serve locally

- Option A (simple):
  - From repo root: `python3 -m http.server 8017 -d .`
  - Open: `http://localhost:8017/web/`

- Option B (any static server):
  - Serve the repo root and navigate to `/web/`.

## Notes

- Uses Pyodide via CDN; requires internet access.
- Loads the project Python sources from `src/` dynamically.
- DB runs in-memory inside the browser tab.

## Quick demo commands

```
CREATE TABLE heroes (id INTEGER, name TEXT, strength INTEGER);
INSERT INTO heroes VALUES (1, 'Arjuna', 95);
INSERT INTO heroes VALUES (2, 'Krishna', 98);
INSERT INTO heroes VALUES (3, 'Bhima', 87);
SELECT * FROM heroes;
SELECT name FROM heroes WHERE strength > 90;
```


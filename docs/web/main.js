// Copy of web/main.js but paths work on GitHub Pages under /mandukyadb/
const statusEl = document.getElementById('status');
const outputEl = document.getElementById('output');
const inputEl = document.getElementById('input');
const runBtn = document.getElementById('run');
const resetBtn = document.getElementById('reset');
const examplesBtn = document.getElementById('examples');

let pyodide;

function append(type, text) {
  const div = document.createElement('div');
  div.className = 'entry';
  div.innerHTML = `<span class="prompt">mandukya> </span><span class="${type}">${escapeHtml(text)}</span>`;
  outputEl.appendChild(div);
  outputEl.scrollTop = outputEl.scrollHeight;
}

function appendResult(text) {
  const pre = document.createElement('pre');
  pre.className = 'entry';
  pre.textContent = text;
  outputEl.appendChild(pre);
  outputEl.scrollTop = outputEl.scrollHeight;
}

function escapeHtml(s) {
  return s.replace(/[&<>\"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));
}

async function loadPyodideAndDB() {
  statusEl.textContent = 'Loading Pyodide…';
  self.pyodide = await import('https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.mjs').then(m => m.loadPyodide({indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/'}));
  pyodide = self.pyodide;
  statusEl.textContent = 'Preparing Python env…';

  await pyodide.runPythonAsync(`import sys\nsys.path.insert(0, '/')`);

  const files = [
    'src/__init__.py',
    'src/cache.py',
    'src/exceptions.py',
    'src/execution.py',
    'src/mandukya_db.py',
    'src/parser.py',
    'src/storage.py'
  ];
  await pyodide.FS.mkdirTree('/src');
  const bust = `v=${Date.now()}`;
  for (const f of files) {
    // On GitHub Pages, docs/web is served under /mandukyadb/web/, so ../src resolves to /mandukyadb/src
    const res = await fetch(`../${f}?${bust}`, {cache: 'no-store'});
    if (!res.ok) throw new Error(`Failed to fetch ${f}`);
    const text = await res.text();
    pyodide.FS.writeFile('/' + f, text);
  }

  await pyodide.runPythonAsync(`
from src.mandukya_db import MandukyaDB
from src.exceptions import MandukyaError
db = MandukyaDB(':memory:')
def run_sql(sql: str):
    return db.execute(sql)
def get_tables():
    return db.get_tables()
def close_db():
    db.close()
  `);

  statusEl.textContent = 'Ready. In-memory DB initialized.';
  append('ok', 'Connected to MandukyaDB (:memory:)');
}

async function resetDB() {
  statusEl.textContent = 'Resetting DB…';
  try { await pyodide.runPythonAsync('close_db()'); } catch {}
  await pyodide.runPythonAsync(`from src.mandukya_db import MandukyaDB\ndb = MandukyaDB(':memory:')`);
  append('ok', 'Database reset to :memory:');
  statusEl.textContent = 'Ready';
}

function stringifyResult(result) {
  if (result == null) return '';
  if (Array.isArray(result)) {
    if (result.length === 0) return '(0 rows)';
    return result.map(r => Array.isArray(r) ? r.join(' | ') : String(r)).join('\n');
  }
  if (typeof result === 'object') return JSON.stringify(result, null, 2);
  return String(result);
}

async function runInput() {
  const text = inputEl.value.trim();
  if (!text) return;
  append('ok', text);
  inputEl.value = '';
  const statements = text.split(';').map(s => s.trim()).filter(Boolean).map(s => s + ';');
  for (const sql of statements) {
    try {
      const py = `\nimport json\ntry:\n    res = run_sql(${JSON.stringify(sql)})\n    def to_json_val(x):\n        try:\n            return json.dumps(x)\n        except TypeError:\n            if isinstance(x, list):\n                y = []\n                for t in x:\n                    if isinstance(t, tuple):\n                        y.append(list(t))\n                    else:\n                        y.append(t)\n                return json.dumps(y)\n            return json.dumps(str(x))\n    print(json.dumps({"ok": True, "result": json.loads(to_json_val(res))}))\nexcept Exception as e:\n    print(json.dumps({"ok": False, "error": str(e)}))`;
      const jsonStr = await pyodide.runPythonAsync(py);
      const payload = JSON.parse(jsonStr);
      if (payload.ok) {
        appendResult(stringifyResult(payload.result));
      } else {
        append('error', payload.error || 'Error');
      }
    } catch (e) {
      const msg = String(e).split('\n').slice(-1)[0];
      append('error', msg || String(e));
    }
  }
}

function loadExamples() {
  inputEl.value = `CREATE TABLE heroes (id INTEGER, name TEXT, strength INTEGER);\nINSERT INTO heroes VALUES (1, 'Arjuna', 95);\nINSERT INTO heroes VALUES (2, 'Krishna', 98);\nINSERT INTO heroes VALUES (3, 'Bhima', 87);\nSELECT * FROM heroes;\nSELECT name FROM heroes WHERE strength > 90;`;
}

runBtn.addEventListener('click', runInput);
resetBtn.addEventListener('click', resetDB);
examplesBtn.addEventListener('click', loadExamples);
inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.shiftKey) { e.preventDefault(); runInput(); }
});

loadPyodideAndDB().catch((e) => { statusEl.textContent = 'Failed to initialize'; append('error', String(e)); });

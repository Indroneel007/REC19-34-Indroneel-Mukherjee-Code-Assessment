import json
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[1] / 'db'
DB_DIR.mkdir(parents=True, exist_ok=True)
META_FILE = DB_DIR / 'metadata.json'
VECTORS_FILE = DB_DIR / 'vectors.json'

def _read(file_path: Path):
    if not file_path.exists():
        return {}
    try:
        return json.loads(file_path.read_text(encoding='utf8') or '{}')
    except Exception:
        return {}

def _write(file_path: Path, obj):
    file_path.write_text(json.dumps(obj, indent=2), encoding='utf8')

def save_metadata(doc_id, meta):
    all = _read(META_FILE)
    all[doc_id] = meta
    _write(META_FILE, all)

def save_vectors(doc_id, items):
    all = _read(VECTORS_FILE)
    all[doc_id] = items
    _write(VECTORS_FILE, all)

def load_vectors(doc_id):
    all = _read(VECTORS_FILE)
    return all.get(doc_id)

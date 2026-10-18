"""Read conversation turns from JSONL, JSON, or SQLite history stores."""
import json
import os
import sqlite3


def _load_jsonl(path):
    turns = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError("history %s line %d: invalid JSON (%s)" % (path, lineno, exc))
            turns.append(_normalize_turn(obj, lineno))
    return turns


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and isinstance(data.get("turns"), list):
        items = data["turns"]
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("history %s: expected a list of turns or {'turns': [...]}" % path)
    return [_normalize_turn(obj, i + 1) for i, obj in enumerate(items)]


def _normalize_turn(obj, idx):
    if not isinstance(obj, dict):
        raise ValueError("turn %d: not an object" % idx)
    role = obj.get("role")
    content = obj.get("content")
    if not isinstance(role, str) or not isinstance(content, str):
        raise ValueError("turn %d: needs string 'role' and 'content'" % idx)
    return {"role": role, "content": content}


def _load_sqlite(path, table=None, role_col=None, content_col=None):
    con = sqlite3.connect(path)
    try:
        cur = con.cursor()
        if table is None:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [r[0] for r in cur.fetchall()]
            candidates = [t for t in tables if t.lower() in ("turns", "messages", "history", "conversations")]
            table = candidates[0] if candidates else (tables[0] if tables else None)
            if table is None:
                raise ValueError("sqlite history %s: no tables found" % path)
        cols = [r[1] for r in cur.execute("PRAGMA table_info(%s)" % table)]
        role_col = role_col or _match_col(cols, ("role",))
        content_col = content_col or _match_col(cols, ("content", "text", "body"))
        if role_col is None or content_col is None:
            raise ValueError("sqlite history %s.%s: need role/content columns, found %s" % (path, table, cols))
        cur.execute("SELECT %s, %s FROM %s" % (role_col, content_col, table))
        return [{"role": str(r[0]), "content": str(r[1])} for r in cur.fetchall()]
    finally:
        con.close()


def _match_col(cols, wanted):
    low = {c.lower(): c for c in cols}
    for w in wanted:
        if w in low:
            return low[w]
    return None


def load_turns(history_path, sqlite_table=None, sqlite_role_col=None, sqlite_content_col=None):
    """Load [(role, content)] turns from JSONL (.jsonl), JSON (.json), or SQLite (.db/.sqlite)."""
    ext = os.path.splitext(history_path)[1].lower()
    if ext == ".jsonl":
        return _load_jsonl(history_path)
    if ext == ".json":
        return _load_json(history_path)
    if ext in (".db", ".sqlite", ".sqlite3"):
        return _load_sqlite(history_path, sqlite_table, sqlite_role_col, sqlite_content_col)
    raise ValueError("unsupported history format (use .jsonl, .json, or .db): %s" % history_path)

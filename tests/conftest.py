"""Fixture builders for history-tamper-guard tests."""
import json
import os
import sqlite3
import pytest

TURNS = [
    {"role": "user", "content": "deploy the new model"},
    {"role": "assistant", "content": "deploying now, will confirm"},
    {"role": "tool", "content": "deploy succeeded at 2026-10-18"},
]


@pytest.fixture
def history_jsonl(tmp_path):
    path = str(tmp_path / "history.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for t in TURNS:
            f.write(json.dumps(t) + "\n")
    return path


@pytest.fixture
def history_json(tmp_path):
    path = str(tmp_path / "history.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"turns": TURNS}, f)
    return path


@pytest.fixture
def history_sqlite(tmp_path):
    path = str(tmp_path / "history.db")
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT)")
    con.executemany("INSERT INTO messages (role, content) VALUES (?, ?)",
                    [(t["role"], t["content"]) for t in TURNS])
    con.commit()
    con.close()
    return path


@pytest.fixture
def ledger_path(tmp_path):
    return str(tmp_path / "ledger.json")

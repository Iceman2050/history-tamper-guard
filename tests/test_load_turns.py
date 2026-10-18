import json
import pytest
from guard.notary import load_turns


def test_load_jsonl(history_jsonl):
    turns = load_turns(history_jsonl)
    assert len(turns) == 3
    assert turns[0] == {"role": "user", "content": "deploy the new model"}


def test_load_json_dict(history_json):
    assert len(load_turns(history_json)) == 3


def test_load_json_list(tmp_path):
    path = str(tmp_path / "h.json")
    json.dump([{"role": "user", "content": "x"}], open(path, "w"))
    assert load_turns(path) == [{"role": "user", "content": "x"}]


def test_load_sqlite(history_sqlite):
    turns = load_turns(history_sqlite)
    assert len(turns) == 3
    assert turns[1]["role"] == "assistant"
    assert "deploy succeeded" in turns[2]["content"]


def test_unsupported_format(tmp_path):
    path = str(tmp_path / "h.csv")
    open(path, "w").write("role,content\n")
    with pytest.raises(ValueError, match="unsupported history format"):
        load_turns(path)


def test_malformed_jsonl_line(tmp_path):
    path = str(tmp_path / "bad.jsonl")
    open(path, "w").write('{"role": "user", "content": "ok"}\n{broken\n')
    with pytest.raises(ValueError, match="line 2"):
        load_turns(path)


def test_turn_missing_fields(tmp_path):
    path = str(tmp_path / "bad.jsonl")
    open(path, "w").write('{"role": "user"}\n')
    with pytest.raises(ValueError, match="turn 1"):
        load_turns(path)


def test_sqlite_no_usable_columns(tmp_path):
    import sqlite3
    path = str(tmp_path / "h.db")
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE junk (a TEXT, b TEXT)")
    con.close()
    with pytest.raises(ValueError, match="need role/content columns"):
        load_turns(path)


def test_empty_jsonl_is_zero_turns(tmp_path):
    path = str(tmp_path / "empty.jsonl")
    open(path, "w").write("")
    assert load_turns(path) == []


def test_extra_fields_stripped(history_jsonl):
    turns = load_turns(history_jsonl)
    assert set(turns[0].keys()) == {"role", "content"}

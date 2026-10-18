import hashlib
import json
import pytest
from guard.ledger import notarize, load_ledger, _turn_hash, _chain_hash, GENESIS


def test_notarize_builds_linked_chain(history_jsonl, ledger_path):
    ledger = notarize(history_jsonl, ledger_path)
    assert len(ledger["entries"]) == 3
    prev = GENESIS
    for e in ledger["entries"]:
        assert e["prev_chain"] == prev
        assert e["chain_hash"] == _chain_hash(e["prev_chain"], e["turn_hash"])
        prev = e["chain_hash"]


def test_turn_hashes_are_deterministic(history_jsonl, ledger_path):
    expected = hashlib.sha256("user\ndeploy the new model".encode()).hexdigest()
    ledger = notarize(history_jsonl, ledger_path)
    assert ledger["entries"][0]["turn_hash"] == expected


def test_notarize_idempotent(history_jsonl, ledger_path):
    notarize(history_jsonl, ledger_path)
    ledger = notarize(history_jsonl, ledger_path)
    assert len(ledger["entries"]) == 3


def test_notarize_appends_only_new_turns(history_jsonl, ledger_path):
    ledger = notarize(history_jsonl, ledger_path)
    prefix = [e["turn_hash"] for e in ledger["entries"]]
    with open(history_jsonl, "a") as f:
        f.write(json.dumps({"role": "user", "content": "new instruction"}) + "\n")
    ledger2 = notarize(history_jsonl, ledger_path)
    assert len(ledger2["entries"]) == 4
    assert [e["turn_hash"] for e in ledger2["entries"]][:3] == prefix


def test_notarize_refuses_edited_history(history_jsonl, ledger_path):
    notarize(history_jsonl, ledger_path)
    lines = open(history_jsonl).read().splitlines()
    lines[1] = json.dumps({"role": "assistant", "content": "do something else entirely"})
    open(history_jsonl, "w").write("\n".join(lines) + "\n")
    with pytest.raises(ValueError, match="run 'verify'"):
        notarize(history_jsonl, ledger_path)


def test_load_ledger_rejects_garbage(tmp_path):
    path = str(tmp_path / "bad.json")
    open(path, "w").write('{"nope": 1}')
    with pytest.raises(ValueError, match="not a compatible"):
        load_ledger(path)


def test_no_mocks_in_tool_code():
    import subprocess, os
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "guard")
    out = subprocess.run(["grep", "-r", "unittest.mock", root], capture_output=True, text=True)
    assert out.returncode != 0, out.stdout


def test_ledger_records_roles(history_jsonl, ledger_path):
    ledger = notarize(history_jsonl, ledger_path)
    assert [e["role"] for e in ledger["entries"]] == ["user", "assistant", "tool"]


def test_seq_numbers_increment(history_jsonl, ledger_path):
    ledger = notarize(history_jsonl, ledger_path)
    assert [e["seq"] for e in ledger["entries"]] == [0, 1, 2]

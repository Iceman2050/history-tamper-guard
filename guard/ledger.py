"""Append-only notary ledger: each turn's SHA-256 chained to the previous hash."""
import hashlib
import json
import os
from datetime import datetime, timezone

from .notary import load_turns

LEDGER_FORMAT_VERSION = 1
GENESIS = "0" * 64


def _turn_hash(role, content):
    return hashlib.sha256(("%s\n%s" % (role, content)).encode("utf-8")).hexdigest()


def _chain_hash(prev_chain, turn_hash):
    return hashlib.sha256(("%s%s" % (prev_chain, turn_hash)).encode("utf-8")).hexdigest()


def _new_ledger(history_path):
    return {
        "format_version": LEDGER_FORMAT_VERSION,
        "history": os.path.abspath(history_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "entries": [],
    }


def load_ledger(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or data.get("format_version") != LEDGER_FORMAT_VERSION:
        raise ValueError("not a compatible history-tamper-guard ledger: %s" % path)
    return data


def save_ledger(ledger, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)
    return path


def notarize(history_path, ledger_path, sqlite_table=None, sqlite_role_col=None, sqlite_content_col=None):
    """Append each turn of the history store to the ledger with chained hashes.

    Returns the ledger dict. Idempotent: re-running only appends genuinely new
    trailing turns (matching the ledger's recorded prefix).
    """
    turns = load_turns(history_path, sqlite_table, sqlite_role_col, sqlite_content_col)
    ledger = load_ledger(ledger_path) if os.path.isfile(ledger_path) else _new_ledger(history_path)
    entries = ledger["entries"]

    start = len(entries)
    if start and turns[:start] and [e["turn_hash"] for e in entries] != [
        _turn_hash(t["role"], t["content"]) for t in turns[:start]
    ]:
        raise ValueError(
            "ledger prefix does not match history store: history was edited after notarization; "
            "run 'verify' to see exactly what changed before notarizing again")

    prev_chain = entries[-1]["chain_hash"] if entries else GENESIS
    for i, turn in enumerate(turns[start:], start):
        th = _turn_hash(turn["role"], turn["content"])
        ch = _chain_hash(prev_chain, th)
        entries.append({
            "seq": i,
            "turn_hash": th,
            "prev_chain": prev_chain,
            "chain_hash": ch,
            "role": turn["role"],
            "notarized_at": datetime.now(timezone.utc).isoformat(),
        })
        prev_chain = ch
    save_ledger(ledger, ledger_path)
    return ledger

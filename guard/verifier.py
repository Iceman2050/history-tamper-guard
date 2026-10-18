"""Verify a history store against its notary ledger; flag tampering."""
from .notary import load_turns
from .ledger import load_ledger, _turn_hash, _chain_hash, GENESIS


def verify(history_path, ledger_path, sqlite_table=None, sqlite_role_col=None, sqlite_content_col=None):
    """Return list of findings: {seq, kind, severity, detail}.

    Kinds: OK (clean re-chain), EDITED (turn content changed), UNRECORDED
    (turns present with no ledger entry), DELETED (ledger entries missing from
    the store), CHAIN_BREAK (ledger's own hashes don't link up).
    """
    turns = load_turns(history_path, sqlite_table, sqlite_role_col, sqlite_content_col)
    ledger = load_ledger(ledger_path)
    entries = ledger["entries"]
    findings = []

    # 1) is the ledger internally consistent? (catches ledger tampering too)
    prev = GENESIS
    for e in entries:
        if e["prev_chain"] != prev or _chain_hash(e["prev_chain"], e["turn_hash"]) != e["chain_hash"]:
            findings.append({"seq": e.get("seq"), "kind": "CHAIN_BREAK", "severity": "high",
                             "detail": "ledger entry seq %s does not chain correctly" % e.get("seq")})
            break
        prev = e["chain_hash"]

    # 2) compare store turns against ledger entries
    n = min(len(turns), len(entries))
    for i in range(n):
        th = _turn_hash(turns[i]["role"], turns[i]["content"])
        if th != entries[i]["turn_hash"]:
            findings.append({
                "seq": i, "kind": "EDITED", "severity": "high",
                "detail": "turn %d (%s) content differs from notarized hash" % (i, turns[i]["role"]),
            })

    if len(turns) > len(entries):
        for i in range(len(entries), len(turns)):
            findings.append({
                "seq": i, "kind": "UNRECORDED", "severity": "high",
                "detail": "turn %d (%s) has no ledger entry — appended or fabricated after notarization" % (i, turns[i]["role"]),
            })
    if len(entries) > len(turns):
        for i in range(len(turns), len(entries)):
            findings.append({
                "seq": i, "kind": "DELETED", "severity": "high",
                "detail": "ledger entry seq %d (%s) is missing from the history store" % (i, entries[i].get("role")),
            })
    return findings

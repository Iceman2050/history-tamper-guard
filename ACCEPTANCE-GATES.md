# ACCEPTANCE GATES — history-tamper-guard (built 2026-10-18)

1. GH-NAME: `gh search repos "history-tamper-guard"` returns no exact-name hit. Check: gh search repos command above. DONE 2026-10-18 (only fuzzy match "timechain-agent").
2. PYTEST: `python -m pytest -v` exits 0 with ≥12 tests passing, including ≥8 exercising core logic (notarize chain, verify edit/delete/fabrication, JSONL + JSON + SQLite). Check: run in dir, capture output.
3. CLI E2E: `notarize` on fixture history JSONL builds ledger with chained hashes; `verify` on clean store = OK; after editing a turn / adding a fabricated assistant turn / deleting a turn / appending a turn, `verify` flags EDITED / UNRECORDED / DELETED correctly. Check: run CLI sequence, grep output.
4. CI: .github/workflows/ci.yml uses checkout@v4, setup-python@v5 (3.12), and `python -m pytest -v` (not bare pytest). Check: grep ci.yml; run the exact CI test command locally.
5. LICENSE: MIT present with "Ingenious AI" attribution line.
6. README: title + 2026-09-24 dated hook with Darktrace source link + how-to-run + "## Built by Ingenious AI" + all 11 platform links + "## What it does NOT do".
7. NO MOCKS IN TOOL CODE: grep for unittest.mock in guard/ == 0 (fixtures in tests only).
8. PUSH: `gh repo create Iceman2050/history-tamper-guard --public --source=<dir> --push --description="<hook>"`; on throttle write PUSH-COMMAND.txt and CONTINUE.

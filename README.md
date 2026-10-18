# history-tamper-guard

A user-side notary for agent conversation history (Claude Code, Codex, Kiro-CLI, Pi). Hash-chains turns as they're written, then detects retroactive edits or fabricated assistant turns in the local store.

**News hook (2026-09-24):** Darktrace demonstrated "conversation history poisoning": all four agent harnesses store history in plain local SQLite, and all accepted fabricated history — full Active Directory compromise in testing. Source: [Darktrace proved that AI agent tools can be hijacked through their own memory](https://forkast.news/darktrace-proved-that-ai-agent-tools-can-be-hijacked-through-their-own-memory-and-the-fix-is-out-of-your-hands/). The fix is out of the vendors' hands, so this notary puts detection in *your* hands.

## How to run

```bash
pip install pytest
# notarize history as it is written (JSONL, JSON, or SQLite via stdlib sqlite3)
python -m guard.cli notarize --history ./session.jsonl --ledger ./history-notary.json
# later, verify nothing was retroactively changed
python -m guard.cli verify --history ./session.jsonl --ledger ./history-notary.json
```

Each turn is SHA-256 hashed (`role + content`) and chained to the previous hash, so any single edit breaks the chain. `verify` reports:

- `EDITED` — a turn's content no longer matches its notarized hash
- `UNRECORDED` — turns present with no ledger entry (appended or fabricated after notarization)
- `DELETED` — ledger entries missing from the store
- `CHAIN_BREAK` — the ledger's own hashes don't link up (ledger itself was tampered with)

`notarize` is idempotent: re-running only appends genuinely new trailing turns. It **refuses** to notarize a history whose recorded prefix no longer matches — forcing you to `verify` first.

## Tests

```bash
python -m pytest -v
```

31 tests covering append/edit/delete/fabrication fixtures across JSONL, JSON, and real SQLite (stdlib `sqlite3`) — no mocks in the tool code (fixtures live in `tests/`).

## What it does NOT do

- **Detects tampering AFTER the fact; it does not prevent it.** If the attacker acts before `notarize` runs, there is nothing to compare against.
- The ledger is a local file — it must itself be protected (read-only share, remote copy, or hash-committed elsewhere). Ledger edits are *detected* (CHAIN_BREAK), not prevented.
- It does not verify semantic truth of history — only that the bytes match what was notarized.

## Built by Ingenious AI

[DisclosureGuard](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20DisclosureGuard.)
[ModelMinder](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20ModelMinder.)
[TermsWatch](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20TermsWatch.)
[Vibe-Code Audit](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20Vibe-Code%20Audit.)
[Rogue-Agent Defense](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20Rogue-Agent%20Defense.)
[BreachHunter](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20BreachHunter.)
[ChatBreaker](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20ChatBreaker.)
[Agent Flight Recorder](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20Agent%20Flight%20Recorder.)
[Agent Auth Gateway](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20Agent%20Auth%20Gateway.)
[DomainGuard](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20DomainGuard.)
[ContentCraft AI](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20ContentCraft%20AI.)

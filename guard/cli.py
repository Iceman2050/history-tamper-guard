"""CLI for history-tamper-guard: notarize | verify."""
import argparse
import sys

from .notary import load_turns
from .ledger import notarize, load_ledger
from .verifier import verify


def _sqlite_args(parser):
    parser.add_argument("--sqlite-table", default=None)
    parser.add_argument("--sqlite-role-col", default=None)
    parser.add_argument("--sqlite-content-col", default=None)


def cmd_notarize(args):
    ledger = notarize(args.history, args.ledger, args.sqlite_table, args.sqlite_role_col, args.sqlite_content_col)
    print("notarized %d turn(s) into %s" % (len(ledger["entries"]), args.ledger))
    return 0


def cmd_verify(args):
    findings = verify(args.history, args.ledger, args.sqlite_table, args.sqlite_role_col, args.sqlite_content_col)
    if not findings:
        print("OK: history matches the notary ledger (%d turns)" % len(load_ledger(args.ledger)["entries"]))
        return 0
    print("TAMPER: %d finding(s)" % len(findings))
    for f in findings:
        print("[%s] seq %s %s: %s" % (f["severity"].upper(), f["seq"], f["kind"], f["detail"]))
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="history-tamper-guard",
                                     description="Notarize agent conversation history; detect retroactive tampering.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, helptext in (("notarize", "hash-chain turns from a history store into the ledger"),
                           ("verify", "compare the store against the ledger and flag tampering")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--history", required=True, help="history file (.jsonl, .json, .db/.sqlite)")
        p.add_argument("--ledger", required=True, help="notary ledger JSON path")
        _sqlite_args(p)
    args = parser.parse_args(argv)
    try:
        return cmd_notarize(args) if args.command == "notarize" else cmd_verify(args)
    except (ValueError, FileNotFoundError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

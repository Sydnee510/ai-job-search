#!/usr/bin/env python3
"""
tracker.py — CSV-backed application tracker for the ai-job-* skills.

Usage:
    python3 tracker.py add --company "Anthropic" --role "EM, Applied AI" \
        --url "https://..." --fit 8 --stage applied \
        --next "follow up 2026-04-23" --notes "warm intro via X"

    python3 tracker.py list
    python3 tracker.py list --stage interviewing
    python3 tracker.py list --min-fit 7

    python3 tracker.py update --id 3 --stage interviewing --next "loop 2026-04-28"
    python3 tracker.py update --id 3 --notes "append: recruiter said H1"

CSV lives at: <project_root>/output/tracker.csv
Default project root is computed from this script's location
(.claude/skills/ai-job-pipeline/tracker.py → ../../..).
Override with env var AI_JOB_PROJECT_ROOT or --csv flag.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
PROJECT_ROOT = Path(os.environ.get("AI_JOB_PROJECT_ROOT", DEFAULT_PROJECT_ROOT))
CSV_PATH = PROJECT_ROOT / "output" / "tracker.csv"

FIELDS = [
    "id",
    "date",
    "company",
    "role",
    "url",
    "fit",
    "stage",
    "next_action",
    "notes",
    "last_updated",
]

VALID_STAGES = {
    "analyzing",
    "drafting",
    "applied",
    "screening",
    "interviewing",
    "offer",
    "rejected",
    "withdrawn",
    "on_hold",
}


def ensure_csv():
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()


def read_rows():
    ensure_csv()
    with CSV_PATH.open("r", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(rows):
    with CSV_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def next_id(rows):
    if not rows:
        return 1
    return max(int(r["id"]) for r in rows) + 1


def today_iso():
    return datetime.date.today().isoformat()


def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")


def cmd_add(args):
    rows = read_rows()
    if args.stage not in VALID_STAGES:
        sys.exit(f"Invalid stage '{args.stage}'. Valid: {sorted(VALID_STAGES)}")
    row = {
        "id": next_id(rows),
        "date": args.date or today_iso(),
        "company": args.company,
        "role": args.role,
        "url": args.url or "",
        "fit": args.fit,
        "stage": args.stage,
        "next_action": args.next or "",
        "notes": args.notes or "",
        "last_updated": now_iso(),
    }
    rows.append(row)
    write_rows(rows)
    print(f"Added row id={row['id']}: {row['company']} — {row['role']} (fit {row['fit']}/10, stage={row['stage']})")


def cmd_list(args):
    rows = read_rows()
    if args.stage:
        rows = [r for r in rows if r["stage"] == args.stage]
    if args.min_fit is not None:
        rows = [r for r in rows if r["fit"] and int(r["fit"]) >= args.min_fit]
    if args.company:
        needle = args.company.lower()
        rows = [r for r in rows if needle in r["company"].lower()]

    if not rows:
        print("(no matching rows)")
        return

    cols = ["id", "date", "company", "role", "fit", "stage", "next_action"]
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    header = " | ".join(c.ljust(widths[c]) for c in cols)
    sep = "-+-".join("-" * widths[c] for c in cols)
    print(header)
    print(sep)
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))


def cmd_update(args):
    rows = read_rows()
    target = None
    for r in rows:
        if int(r["id"]) == args.id:
            target = r
            break
    if target is None:
        sys.exit(f"No row with id={args.id}")

    if args.stage:
        if args.stage not in VALID_STAGES:
            sys.exit(f"Invalid stage '{args.stage}'. Valid: {sorted(VALID_STAGES)}")
        target["stage"] = args.stage
    if args.next is not None:
        target["next_action"] = args.next
    if args.notes is not None:
        if args.notes.startswith("append:"):
            addition = args.notes[len("append:"):].strip()
            target["notes"] = (target["notes"] + " | " + addition).strip(" |")
        else:
            target["notes"] = args.notes
    if args.fit is not None:
        target["fit"] = args.fit
    if args.url is not None:
        target["url"] = args.url

    target["last_updated"] = now_iso()
    write_rows(rows)
    print(f"Updated row id={args.id}: stage={target['stage']}, next={target['next_action']!r}")


def build_parser():
    p = argparse.ArgumentParser(description="ai-job-apply tracker CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add", help="add a new application row")
    add.add_argument("--company", required=True)
    add.add_argument("--role", required=True)
    add.add_argument("--url", default="")
    add.add_argument("--fit", type=int, required=True, help="1-10 overall fit score")
    add.add_argument("--stage", default="applied",
                     help=f"one of {sorted(VALID_STAGES)}")
    add.add_argument("--next", default="", dest="next", help="next action")
    add.add_argument("--notes", default="")
    add.add_argument("--date", default="", help="ISO date, defaults to today")
    add.set_defaults(func=cmd_add)

    lst = sub.add_parser("list", help="list applications")
    lst.add_argument("--stage", help="filter by stage")
    lst.add_argument("--min-fit", type=int, dest="min_fit", help="minimum fit score")
    lst.add_argument("--company", help="substring match on company")
    lst.set_defaults(func=cmd_list)

    upd = sub.add_parser("update", help="update an existing row by id")
    upd.add_argument("--id", type=int, required=True)
    upd.add_argument("--stage")
    upd.add_argument("--next", dest="next")
    upd.add_argument("--notes", help="use 'append: <text>' to append rather than replace")
    upd.add_argument("--fit", type=int)
    upd.add_argument("--url")
    upd.set_defaults(func=cmd_update)

    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

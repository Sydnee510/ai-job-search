#!/usr/bin/env python3
"""
discover.py — poll company ATSes for open roles matching user_profile.targeting.target_job_titles.

Sources (in order of reliability):
  1. Greenhouse boards API   — https://boards-api.greenhouse.io/v1/boards/{id}/jobs
  2. Lever postings API       — https://api.lever.co/v0/postings/{id}?mode=json
  3. Ashby public job board   — https://api.ashbyhq.com/posting-api/job-board/{id}

For each company in <project_root>/knowledge/company_ats.json:
  - If ats is set, poll that ATS.
  - If ats is null or the mapped ATS 404s, probe Greenhouse → Lever → Ashby in order.
  - Cache any discovered mapping back to the JSON file.

Title filter is built at load time from user_profile.json's targeting.target_job_titles.
Rank by tier × title specificity × freshness × remote-friendly.
Emit JSON to stdout (default) or a file with --output.

Stdlib only. No external deps.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
PROJECT_ROOT = Path(os.environ.get("AI_JOB_PROJECT_ROOT", DEFAULT_PROJECT_ROOT))
ATS_CONFIG = PROJECT_ROOT / "knowledge" / "company_ats.json"
USER_PROFILE = PROJECT_ROOT / "knowledge" / "user_profile.json"

HTTP_TIMEOUT = 10


def _load_user_profile() -> dict:
    """Load knowledge/user_profile.json. Missing/invalid file returns an empty dict."""
    if not USER_PROFILE.exists():
        return {}
    try:
        with USER_PROFILE.open() as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _build_user_agent() -> str:
    """UA contact is pulled from user_profile.agent_runtime.user_agent_contact.
    Falls back to a generic UA if unset or empty."""
    profile = _load_user_profile()
    contact = (profile.get("agent_runtime") or {}).get("user_agent_contact") or ""
    contact = contact.strip()
    if contact:
        return f"ai-job-discover/1.0 (+{contact})"
    return "ai-job-discover/1.0"


USER_AGENT = _build_user_agent()

# ---------- Title filtering ----------
#
# Title-inclusion patterns are BUILT FROM user_profile.targeting.target_job_titles
# at module load time. If your profile lists "Senior AI Engineer" and "UX Designer",
# only those roles (and their word-boundary variants) will match.
#
# EXCLUDE_PATTERNS is the static backstop — titles we always drop regardless of
# partial matches. Edit these if your target title collides with a common
# excluded one (e.g. if you target "Product Designer" you may need to loosen
# the "product manager" exclusion, though those strings shouldn't collide).
#
# AI_BOOST_PATTERNS scores matching titles higher on the ranking. Edit for your
# specialty — e.g. add r"\bsecurity\b" for security roles, r"\bdesigner\b" for
# design, etc. Keep it narrow: too many boosts flattens the ranking signal.


def _build_title_include_patterns() -> list[str]:
    """Build regex patterns from user_profile.targeting.target_job_titles.
    Each title is lowercased, tokenized on whitespace, and joined with \\s+ so
    'Senior AI Engineer' matches 'Senior  AI Engineer' and 'Senior, AI Engineer'."""
    profile = _load_user_profile()
    titles = (profile.get("targeting") or {}).get("target_job_titles") or []
    patterns: list[str] = []
    for raw in titles:
        if not isinstance(raw, str) or not raw.strip():
            continue
        tokens = [re.escape(tok) for tok in raw.split()]
        if not tokens:
            continue
        patterns.append(r"\b" + r"\s*,?\s+".join(tokens) + r"\b")
    return patterns


# Fallback title patterns used if user_profile.json is missing or empty.
# Loose by design — any title containing "engineer", "designer", "manager",
# etc. will match. User edits user_profile.json to narrow this.
FALLBACK_TITLE_PATTERNS = [
    r"\bengineer\b",
    r"\bdesigner\b",
    r"\bmanager\b",
    r"\bdirector\b",
    r"\bscientist\b",
    r"\banalyst\b",
    r"\barchitect\b",
    r"\bresearcher\b",
    r"\badvocate\b",
    r"\bhead\s+of\b",
    r"\blead\b",
]

TITLE_INCLUDE_PATTERNS = _build_title_include_patterns() or FALLBACK_TITLE_PATTERNS

# Titles to exclude regardless of matches above. Sales / HR / office manager
# roles sometimes leak through when users target "Manager" titles.
EXCLUDE_PATTERNS = [
    r"\bsales\s+manager\b",
    r"\bmarketing\s+manager\b",
    r"\bcustomer\s+success\s+manager\b",
    r"\baccount\s+manager\b",
    r"\boffice\s+manager\b",
    r"\bpeople\s+manager\b",
    r"\bpartner\s+manager\b",
    r"\bcommunity\s+manager\b",
    r"\brecruiting\s+manager\b",
    r"\bhr\s+manager\b",
    r"\btalent\s+manager\b",
    r"\bengagement\s+manager\b",
]

TITLE_INCLUDE_RE = re.compile("|".join(TITLE_INCLUDE_PATTERNS), re.IGNORECASE)
EXCLUDE_RE = re.compile("|".join(EXCLUDE_PATTERNS), re.IGNORECASE)

# Titles that deserve a score bump. Defaults lean AI — edit to match your field.
# E.g. for security, swap in r"\bsecurity\b", r"\bappsec\b", r"\bcloud\s+security\b".
AI_BOOST_PATTERNS = [
    r"\bai\b", r"\bml\b", r"\bllm\b", r"\bapplied\s+ai\b",
    r"\bagent", r"\bagentic\b",
    r"\bplatform\b", r"\binfra", r"\binference\b",
    r"\bfoundational\b", r"\bmodel\b",
]
AI_BOOST_RE = re.compile("|".join(AI_BOOST_PATTERNS), re.IGNORECASE)

REMOTE_RE = re.compile(r"\bremote\b|\banywhere\b|\bworldwide\b", re.IGNORECASE)


# ---------- Preferences ----------

def load_preferences() -> dict:
    """Load location + compensation preferences from knowledge/user_profile.json.
    Missing file or missing sections return empty defaults."""
    profile = _load_user_profile()
    if not profile:
        return {"locations": [], "hybrid_ok": True, "compensation": {}}
    return {
        "locations": profile.get("locations", []),
        "hybrid_ok": profile.get("hybrid_ok", True),
        "compensation": profile.get("compensation", {}),
    }


def match_location(location_str: str, prefs: dict) -> dict:
    """Return the first matching preference dict for the given location string, or {}.
    Match is case-insensitive and uses word boundaries, so short aliases like 'GA' or 'SF'
    don't false-match 'Bangalore' or 'Sofia'."""
    if not location_str:
        return {}
    hay = location_str.lower()
    for loc in prefs.get("locations", []):
        needles = [loc.get("name", "")] + list(loc.get("aliases", []))
        for n in needles:
            if not n:
                continue
            pattern = r"\b" + re.escape(n.lower()) + r"\b"
            if re.search(pattern, hay):
                return loc
    return {}


def is_target_title(title: str) -> bool:
    """True if the posting title matches one of the user's target_job_titles
    and is not in EXCLUDE_PATTERNS."""
    if not title:
        return False
    if EXCLUDE_RE.search(title):
        return False
    return bool(TITLE_INCLUDE_RE.search(title))


# ---------- HTTP helper ----------

def http_get_json(url: str) -> tuple[int, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            status = r.getcode()
            body = r.read().decode("utf-8", errors="replace")
            try:
                return status, json.loads(body)
            except json.JSONDecodeError:
                return status, None
    except urllib.error.HTTPError as e:
        return e.code, None
    except (urllib.error.URLError, TimeoutError, ConnectionError, socket.timeout, ssl.SSLError, OSError):
        return 0, None


# ---------- ATS adapters ----------

def fetch_greenhouse(board_id: str) -> list[dict]:
    """Greenhouse public boards API. Returns list of Jobs with standardized fields."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_id}/jobs"
    status, data = http_get_json(url)
    if status != 200 or not isinstance(data, dict) or "jobs" not in data:
        return []
    results = []
    for j in data.get("jobs", []):
        loc = (j.get("location") or {}).get("name", "")
        dept_names = [d.get("name", "") for d in (j.get("departments") or [])]
        office_names = [o.get("name", "") for o in (j.get("offices") or [])]
        results.append(
            {
                "title": j.get("title", ""),
                "url": j.get("absolute_url", ""),
                "location": loc,
                "departments": dept_names,
                "offices": office_names,
                "updated_at": j.get("updated_at", ""),
                "source": "greenhouse",
                "source_job_id": str(j.get("id", "")),
            }
        )
    return results


def fetch_lever(board_id: str) -> list[dict]:
    """Lever postings API. Public JSON endpoint."""
    url = f"https://api.lever.co/v0/postings/{board_id}?mode=json"
    status, data = http_get_json(url)
    if status != 200 or not isinstance(data, list):
        return []
    results = []
    for j in data:
        cats = j.get("categories") or {}
        results.append(
            {
                "title": j.get("text", ""),
                "url": j.get("hostedUrl", "") or j.get("applyUrl", ""),
                "location": cats.get("location", ""),
                "departments": [cats.get("team", "")] if cats.get("team") else [],
                "offices": [],
                "updated_at": _ms_to_iso(j.get("createdAt")),
                "source": "lever",
                "source_job_id": j.get("id", ""),
            }
        )
    return results


def fetch_ashby(board_id: str) -> list[dict]:
    """Ashby public job-board API."""
    url = f"https://api.ashbyhq.com/posting-api/job-board/{board_id}?includeCompensation=false"
    status, data = http_get_json(url)
    if status != 200 or not isinstance(data, dict) or "jobs" not in data:
        return []
    results = []
    for j in data.get("jobs", []):
        loc = j.get("locationName") or ""
        if not loc:
            # address may be missing, null, or a dict — coerce safely
            addr = j.get("address") or {}
            postal = addr.get("postalAddress") if isinstance(addr, dict) else None
            if isinstance(postal, dict):
                loc = postal.get("addressRegion") or postal.get("addressLocality") or ""
        results.append(
            {
                "title": j.get("title", ""),
                "url": j.get("jobUrl", ""),
                "location": loc,
                "departments": [j.get("departmentName", "")] if j.get("departmentName") else [],
                "offices": [j.get("teamName", "")] if j.get("teamName") else [],
                "updated_at": j.get("publishedAt", "") or j.get("updatedAt", ""),
                "source": "ashby",
                "source_job_id": j.get("id", ""),
            }
        )
    return results


def _ms_to_iso(ms: Any) -> str:
    try:
        return datetime.datetime.fromtimestamp(int(ms) / 1000, tz=datetime.timezone.utc).isoformat()
    except (TypeError, ValueError):
        return ""


ATS_FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
}


# ---------- Probe fallback ----------

PROBE_ORDER = ["greenhouse", "lever", "ashby"]


def probe_company(board_id: str) -> tuple[str | None, list[dict]]:
    """Try each ATS in order. Return (winning_ats, jobs) or (None, [])."""
    for ats in PROBE_ORDER:
        jobs = ATS_FETCHERS[ats](board_id)
        if jobs:
            return ats, jobs
    return None, []


# ---------- Ranking ----------

def freshness_days(updated_at: str) -> float:
    if not updated_at:
        return 999.0
    try:
        dt = datetime.datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    except ValueError:
        return 999.0
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return max(0.0, (now - dt).total_seconds() / 86400)


def score_job(job: dict, company_tier: int, prefs: dict | None = None) -> tuple[int, dict]:
    """Return (score, annotations) where annotations is extra fields to merge onto the job:
       - location_match: canonical preference name (or "")
       - location_weight: the weight contribution from location
       - needs_comp_verification: bool (True if preference has a min_base_usd set)
    """
    score = 0
    ann: dict = {"location_match": "", "location_weight": 0, "needs_comp_verification": False}

    # Tier bump
    tier_bonus = {1: 10, 2: 5, 3: 3}.get(company_tier, 0)
    score += tier_bonus
    # AI/ML title specificity
    title = job.get("title", "")
    if AI_BOOST_RE.search(title):
        score += 4
    # Exact target-title match (stronger than a partial match)
    if re.search(r"\bengineering\s+manager\b|\bai\s+engineer\b|\bml\s+engineer\b", title, re.IGNORECASE):
        score += 3
    # Freshness
    days = freshness_days(job.get("updated_at", ""))
    if days <= 7:
        score += 5
    elif days <= 30:
        score += 2
    # Remote friendly (baseline bump — may be overridden by prefs below)
    location_str = job.get("location", "") or ""
    offices = " ".join(o for o in (job.get("offices") or []) if o)
    combined_loc = f"{location_str} {offices}".strip()
    if REMOTE_RE.search(combined_loc):
        score += 3

    # Location preferences
    if prefs:
        match = match_location(combined_loc, prefs)
        if match:
            w = int(match.get("weight", 0))
            score += w
            ann["location_match"] = match.get("name", "")
            ann["location_weight"] = w
            if match.get("min_base_usd"):
                ann["needs_comp_verification"] = True
                ann["min_base_usd"] = match["min_base_usd"]

    return score, ann


# ---------- Orchestration ----------

def load_config() -> dict:
    if not ATS_CONFIG.exists():
        sys.exit(f"Config not found: {ATS_CONFIG}")
    with ATS_CONFIG.open() as f:
        return json.load(f)


def save_config(cfg: dict) -> None:
    with ATS_CONFIG.open("w") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")


def fetch_one_company(company: dict) -> tuple[dict, str | None, list[dict], str | None]:
    """Returns (company, used_ats, jobs, warning_or_None)."""
    slug = company["slug"]
    mapped_ats = company.get("ats")
    board_id = company.get("board_id") or slug

    # Try mapped ATS with configured board_id first
    if mapped_ats and mapped_ats in ATS_FETCHERS:
        jobs = ATS_FETCHERS[mapped_ats](board_id)
        if jobs:
            return company, mapped_ats, jobs, None

    # If mapped returned nothing, probe — unless probe is explicitly disabled
    if "notes" in company and "Probe disabled" in company.get("notes", ""):
        return company, None, [], f"{slug}: probe disabled (per notes field); skipping"

    # Probe with configured board_id, then fall back to slug if different
    candidates = [board_id]
    if slug != board_id:
        candidates.append(slug)

    for cand in candidates:
        used_ats, jobs = probe_company(cand)
        if used_ats is not None:
            # Remember the winning board_id too (it may differ from the configured one)
            company["_discovered_board_id"] = cand
            return company, used_ats, jobs, None

    if mapped_ats:
        return company, None, [], f"{slug}: mapped ATS '{mapped_ats}' (board_id={board_id}) returned no jobs; probe tried {candidates} × {PROBE_ORDER}"
    return company, None, [], f"{slug}: no ATS responded (probe tried {candidates} × {PROBE_ORDER})"


def _parse_since(since: str | None) -> datetime.datetime | None:
    """Parse a YYYY-MM-DD string into a UTC-aware datetime at 00:00:00. Returns None if input is None."""
    if not since:
        return None
    try:
        d = datetime.date.fromisoformat(since)
    except ValueError:
        sys.exit(f"--since must be YYYY-MM-DD, got: {since!r}")
    return datetime.datetime.combine(d, datetime.time.min, tzinfo=datetime.timezone.utc)


def _role_updated_at(updated_at: str) -> datetime.datetime | None:
    """Parse a role's updated_at ISO string into a UTC-aware datetime, or None if unparseable."""
    if not updated_at:
        return None
    try:
        dt = datetime.datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def discover(parallelism: int = 8, since: str | None = None) -> dict:
    cfg = load_config()
    prefs = load_preferences()
    companies = cfg.get("companies", [])
    since_dt = _parse_since(since)

    all_roles: list[dict] = []
    warnings: list[str] = []
    mapping_updates: list[tuple[str, str, str | None]] = []  # (slug, discovered_ats, discovered_board_id)
    start = time.time()

    with ThreadPoolExecutor(max_workers=parallelism) as pool:
        futures = {pool.submit(fetch_one_company, c): c for c in companies}
        for fut in as_completed(futures):
            company, used_ats, jobs, warning = fut.result()
            slug = company["slug"]
            tier = company.get("tier", 0)
            display = company.get("display", slug)

            if warning:
                warnings.append(warning)

            # Record auto-discovered mapping if different from config
            discovered_board_id = company.pop("_discovered_board_id", None)
            if used_ats and (company.get("ats") != used_ats or (discovered_board_id and discovered_board_id != company.get("board_id"))):
                mapping_updates.append((slug, used_ats, discovered_board_id))

            # Filter titles + score
            for j in jobs:
                if not is_target_title(j["title"]):
                    continue
                score, ann = score_job(j, tier, prefs)
                all_roles.append({
                    "company": display,
                    "company_slug": slug,
                    "tier": tier,
                    "title": j["title"],
                    "url": j["url"],
                    "location": j.get("location", ""),
                    "departments": j.get("departments", []),
                    "updated_at": j.get("updated_at", ""),
                    "source": j["source"],
                    "score": score,
                    "location_match": ann["location_match"],
                    "location_weight": ann["location_weight"],
                    "needs_comp_verification": ann["needs_comp_verification"],
                    **({"min_base_usd": ann["min_base_usd"]} if "min_base_usd" in ann else {}),
                })

    # Apply discovered mappings to config
    if mapping_updates:
        for slug, ats, board_id in mapping_updates:
            for c in cfg.get("companies", []):
                if c["slug"] == slug:
                    c["ats"] = ats
                    if board_id and board_id != c.get("board_id"):
                        c["board_id"] = board_id
                    c["confidence"] = "probe_verified"
        save_config(cfg)

    # Sort by score descending, then by freshness
    all_roles.sort(key=lambda r: (-r["score"], freshness_days(r["updated_at"])))

    # Apply --since filter (post-sort, so we keep ranking but show only rows updated since the cutoff)
    total_before_since = len(all_roles)
    if since_dt is not None:
        all_roles = [
            r for r in all_roles
            if (dt := _role_updated_at(r.get("updated_at", ""))) is not None and dt >= since_dt
        ]

    elapsed = time.time() - start

    # Tally preference matches for reporting
    pref_summary = {}
    for r in all_roles:
        m = r.get("location_match")
        if m:
            pref_summary[m] = pref_summary.get(m, 0) + 1

    return {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "companies_polled": len(companies),
        "roles_found": len(all_roles),
        "roles_found_before_since_filter": total_before_since,
        "since_filter": since,
        "mapping_updates": [{"slug": s, "ats": a, "board_id": b} for s, a, b in mapping_updates],
        "warnings": warnings,
        "elapsed_seconds": round(elapsed, 2),
        "preferences_applied": {
            "locations": [l.get("name") for l in prefs.get("locations", [])],
            "matches_by_location": pref_summary,
            "comp_flagged_count": sum(1 for r in all_roles if r.get("needs_comp_verification")),
        },
        "roles": all_roles,
    }


# ---------- CLI ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Discover open roles matching user_profile.target_job_titles across target company ATSes")
    p.add_argument("--output", type=Path, help="write JSON to this path (default: stdout)")
    p.add_argument("--parallelism", type=int, default=8, help="concurrent ATS requests (default 8)")
    p.add_argument("--pretty", action="store_true", help="pretty-print JSON")
    p.add_argument(
        "--since",
        type=str,
        metavar="YYYY-MM-DD",
        help="only include roles whose ATS updated_at is on or after this date (UTC). Useful for weekly reviews.",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    result = discover(parallelism=args.parallelism, since=args.since)
    js = json.dumps(result, indent=2 if args.pretty else None)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(js + "\n")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(js)
    # Summary to stderr (so piping stdout to a file still gives a summary in the terminal)
    since_note = ""
    if args.since:
        since_note = (
            f" ({result['roles_found']} after --since {args.since}, "
            f"{result['roles_found_before_since_filter']} total before filter)"
        )
    print(
        f"\nSummary: polled {result['companies_polled']} companies, "
        f"found {result['roles_found']} matching roles{since_note}, "
        f"{len(result['warnings'])} warnings, "
        f"{result['elapsed_seconds']}s elapsed.",
        file=sys.stderr,
    )
    if result["mapping_updates"]:
        print(
            "Updated ATS mappings: " + ", ".join(
                f"{u['slug']}→{u['ats']}" + (f" (board_id={u['board_id']})" if u.get("board_id") else "")
                for u in result["mapping_updates"]
            ),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()

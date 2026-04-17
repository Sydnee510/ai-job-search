---
name: ai-job-discover
description: Discover open roles matching the user's target_job_titles (any field — AI Engineer, PM, UX Designer, SWE, TPM, Security Analyst, etc.) by polling company ATSes directly (Greenhouse, Lever, Ashby) and running targeted web searches. Produces a ranked markdown report of fresh postings, creates tracker rows (stage=analyzing) for each so ai-job-apply can pick them up, and auto-updates the ATS mapping file when new companies are probed.
when_to_use: |
  Triggers: "find me jobs", "what roles are open", "discover new roles",
  "search for jobs this week", "who's hiring [role]", or any
  aggregate-discovery query that is not about a specific company.
allowed-tools: WebSearch WebFetch Read Write Bash(python3 *)
argument-hint: [optional-keyword-filter]
---

# ai-job-discover

**Job-to-be-done:** find open AI-related roles the user hasn't seen yet, ranked by fit, with URLs ready for `ai-job-apply`. Runs weekly (or on demand) and feeds the top of the application funnel.

## User profile (auto-injected at skill load)

```!
cat knowledge/user_profile.json
```

The profile above drives this skill: `targeting.target_job_titles` controls which ATS postings count; `locations[]` + `compensation` drive ranking and comp-verification flags; `agent_runtime.user_agent_contact` sets the HTTP UA.

## Skill input

The user invoked this skill with: `$ARGUMENTS`

If empty, run the default full sweep across all target companies. If non-empty, treat the value as a keyword filter and narrow the WebSearch queries toward it (e.g. a specialty keyword, a city name, "remote", or a specific company name).

## When this skill applies

Triggers:
- "Find me jobs" / "find me some AI roles"
- "What AI roles opened this week"
- "Discover new roles"
- "Who's hiring AI [engineers / PMs / designers / researchers / managers] right now"
- "Search for [family] jobs"
- Any aggregate-discovery query that isn't about a specific company

**NOT this skill:**
- "Help me apply to [specific URL]" → `ai-job-apply`
- "Prep me for [company] interview" → `ai-job-interview-prep`
- "Show me my pipeline" → `ai-job-pipeline`
- "Submit the [company] application" → `ai-job-submit`

## How it works (two-track discovery)

This skill runs **two parallel discovery tracks** and merges their results. Each track covers what the other misses.

### Track A — Direct ATS polling (via `discover.py`)

Hits company ATSes directly through their public JSON APIs. Highest reliability, most authoritative source, covers ~80% of value.

- **Greenhouse** (`boards-api.greenhouse.io/v1/boards/{id}/jobs`)
- **Lever** (`api.lever.co/v0/postings/{id}?mode=json`)
- **Ashby** (`api.ashbyhq.com/posting-api/job-board/{id}`)

Target list + ATS mappings live in `knowledge/company_ats.json`. When a company's ATS guess is wrong, the script auto-probes the other two and caches the correction back to the file — so it gets better over time.

### Track B — WebSearch discovery (via Claude's WebSearch)

Catches what the target list misses: new companies, stealth roles, YC recent batches, non-ATS postings.

Run 2–3 targeted searches per invocation. Construct queries from `user.targeting.target_job_titles`:

1. `WebSearch("{primary target title} AI site:linkedin.com/jobs")` — LinkedIn aggregation (noisy but discovery-rich)
2. `WebSearch("\"{primary target title}\" \"AI\" OR \"ML\" hiring {current year}")` — broad freshness search
3. `WebSearch("Hacker News who is hiring")` (monthly) — catch YC + stealth startups

Filter results to: fresh (< 30 days ideally), titles matching `user.targeting.target_job_titles` or related seniority levels, AI/ML-relevant company. Dedupe against Track A's URLs.

## Inputs

All optional:

- **Keyword filter** — if the user says "find me RAG-specific roles" or any other specialty, narrow the WebSearch queries toward that keyword
- **Minimum tier** — default is all tiers from `knowledge/company_ats.json`
- **Freshness cap** — default is "posted in last 30 days" for ranking, but include all

If no args, run the default full sweep.

## Pipeline (run in order)

### Step 1 — Run direct ATS poll

Output paths follow `knowledge/output_conventions.md`. Create the date directory first (`mkdir -p output/{YYYY-MM-DD}`), then:

```bash
python3 .claude/skills/ai-job-discover/discover.py \
  --output output/{YYYY-MM-DD}/_discover_raw.json \
  --pretty
```

**For weekly reviews, narrow to fresh roles only** with `--since YYYY-MM-DD`. Pass last week's Monday (or whenever the previous discovery run was) so you only see roles the ATSes updated since you last looked:

```bash
python3 .claude/skills/ai-job-discover/discover.py \
  --output output/{YYYY-MM-DD}/_discover_raw.json \
  --since {one-week-ago YYYY-MM-DD} \
  --pretty
```

The output JSON includes `since_filter` and `roles_found_before_since_filter` so the report can show "X new roles since last week (Y total in the funnel)".

Capture:
- `roles_found`, `companies_polled`, `warnings`, `elapsed_seconds` from summary
- Full `roles` array from the JSON file

If warnings mention companies returning no jobs, note them for the user (they may need board_id correction in `knowledge/company_ats.json`). Don't fail the whole run over a few warning rows.

### Step 2 — Run WebSearch discovery (Track B)

Execute 2–3 WebSearch calls tailored to the user's query. Build queries from `user.targeting.target_job_titles`:

- If user supplied a specialty keyword (e.g. "RAG", "evals", "agents"), include it in one query
- Always include a generic query against their primary target title (e.g. "Engineering Manager AI hiring" or "Senior AI Engineer hiring")
- Optionally include `site:linkedin.com/jobs` to aggregate LinkedIn postings

For each search, read the top 10 results. Keep rows where:
- URL is a real job posting (not a listicle, blog post, or company homepage)
- Title matches one of `user.targeting.target_job_titles` or a known seniority variant
- Role appears to be AI/ML/AI-adjacent
- Role is < 30 days old if a date is visible (prefer fresher)

Each Track B entry needs these fields to merge cleanly:
- company (best-effort extraction from URL/snippet)
- title
- url
- location (if available)
- source: "websearch:linkedin" / "websearch:general" / "websearch:hn" / "websearch:{custom}"
- score: compute similar to Track A — start at 10 (unknown tier baseline), +4 if title is AI-titled, +3 if the target title matches exactly, +3 if remote-friendly, THEN add location_weight from `user_profile.locations[]` the same way discover.py does (word-boundary alias match against the location string)
- If the matched location preference has `min_base_usd`, set `needs_comp_verification: true` on the entry

**Enterprise / custom-ATS sources (handled in Track B only):**
Entries in `company_ats.json` with `"ats": null` and a "Probe disabled" note are skipped by the script. Pick them up via targeted WebSearch instead if they're on the user's priority list. Example pattern:
- `WebSearch("site:{careers-domain} '{primary target title}' (AI OR ML)")`
Only include results that are real job postings (not generic careers pages).

### Step 3 — Merge, dedupe, rank

- Concatenate Track A + Track B
- Dedupe by URL (exact match)
- Dedupe by (company, title) approximate match — if same company + same title, keep the one with the higher score (usually Track A since it has tier data)
- Sort by score descending, then by freshness (newer first)

### Step 4 — Cross-reference tracker

- Load `output/tracker.csv` if it exists
- For each role in the merged list, check if its URL already appears in the tracker
- Mark roles as `new` / `already_tracked`
- New roles are the focus of this run

### Step 5 — Write the report

Save to `output/{YYYY-MM-DD}/discover.md` per `knowledge/output_conventions.md` (cross-company artifact, lives at the date level — no company subfolder):

```markdown
# Job Discovery — {today's date}

**Polled:** {N} target companies + {K} WebSearch queries
**Found:** {total} roles matching target titles
**New (not in tracker):** {new_count}
**Elapsed:** {seconds}s

## Location priorities applied
{render from user_profile.locations — e.g. "Remote (+10) · NYC (+7) · SF (+5, verify >=$200k)"}
This run: {location name} {count} · ... (flagged for comp: {f})

## Top new roles (ranked by fit)

### 1. [Company: Role Title](https://...)
- **Score:** 24 | **Tier 1** | **AI-native** | **Remote-friendly**
- Posted: {date}
- Source: greenhouse
- Location: {location}
- ⚠ COMP >= ${X}k — verify base before applying  (if applicable)

### 2. ...

[continue through all new roles]

## Location-preference rollups

Surface any location-preference-specific sub-lists worth calling out:
- **{Top-preference location} roles:** all roles where `location_match == "{top preference}"`
- **Notable remote-friendly roles outside preferred cities** if the user is remote-first

## Already in tracker (for reference)
- [Company — Role](url) — row id, current stage

## ATS mapping updates (auto-applied)
- {company}: {old ats} → {new ats}

## Warnings (fix in `knowledge/company_ats.json` if these matter)
- {company}: {warning}

## Suggested next actions
1. Apply to rows 1–5 this week (one per day)
2. Verify `board_id` for warned companies if any are Tier 1 targets
3. Add any missing companies (from WebSearch) to `company_ats.json` for next run
```

### Step 6 — Create tracker rows for new roles

For each NEW role (not already tracked), create a tracker row with `stage=analyzing`:

```bash
python3 .claude/skills/ai-job-pipeline/tracker.py add \
  --company "{company}" \
  --role "{title}" \
  --url "{url}" \
  --fit {score_as_fit_proxy} \
  --stage analyzing \
  --next "review + decide to apply" \
  --notes "discovered {date} via {source}"
```

Where `fit` is derived from `score`:
- score ≥ 18 → fit = 8
- score 12–17 → fit = 7
- score 6–11 → fit = 6
- score < 6 → fit = 5

These are provisional fits. The user's next invocation of `ai-job-apply` will compute a real 5-dimension fit score from the JD.

### Step 7 — Report summary

Tell the user:
- "{N} new roles added to your pipeline. Top 3: {list}."
- "To apply to one, say `help me apply to {company} {role}` or paste its URL."
- If warnings are non-trivial, list companies that need `board_id` correction.
- If ATS mappings were auto-updated, mention which.

## Skill-internal assets

- `discover.py` — ATS orchestrator (stdlib only). Parses `company_ats.json`, polls Greenhouse/Lever/Ashby in parallel, filters to titles matching the user's target patterns, ranks, writes JSON.

## Shared knowledge this skill reads + writes

- `knowledge/user_profile.json` — READ. Target titles, locations, comp gates, agent UA.
- `knowledge/company_ats.json` — READ + WRITE. Source of truth for target companies + their ATS mappings. Script auto-updates when probes succeed.
- `knowledge/target_companies.md` — READ only. For tier classification and warmth notes (useful when merging WebSearch hits against the known list).
- `knowledge/writing_voice.md` — READ only, applied to the summary report.
- `knowledge/output_conventions.md` — READ only. Required path layout for `discover.md` and `_discover_raw.json` (date folder, no company subfolder).
- `output/tracker.csv` — READ via `ai-job-pipeline/tracker.py list`, WRITE via `tracker.py add`. Stays at project root (cumulative).

## How location preferences affect ranking

`user_profile.locations` (in `knowledge/user_profile.json`) is an ordered list of locations with a `weight` each. `discover.py` adds that weight to the role's score when the role's location matches (word-boundary, case-insensitive). Any location with a `min_base_usd` field flags matching roles as `needs_comp_verification: true` in the output JSON — those appear in the report with a `COMP >= ${X}k` tag so the user verifies base pay before applying.

Matching uses the canonical name plus the `aliases` array. Aliases are matched at word boundaries to prevent short aliases (e.g. `"GA"`) from false-matching unrelated strings.

When the user says "find me {city} roles" or similar location-narrowed query, after the script runs, filter the merged list (Track A + Track B) down to roles where `location_match == "{city}"` or the location string contains a matching signal.

## Critical behaviors

- **Output paths are non-negotiable.** Discovery report goes to `output/{YYYY-MM-DD}/discover.md` and raw JSON to `output/{YYYY-MM-DD}/_discover_raw.json` per `knowledge/output_conventions.md`. Tracker stays at `output/tracker.csv`. Create the date directory with `mkdir -p` before writing.
- **Voice rules apply** to the report prose. Re-read `knowledge/writing_voice.md`. No em-dashes in the generated markdown. Short, scannable.
- **Never auto-apply.** Discovery surfaces candidates. The user picks. Applications run through `ai-job-apply` separately.
- **Never write misleading tracker data.** New rows are always `stage=analyzing`, not `applied`. The user advances them after reviewing.
- **Be honest about source quality.** Track A (direct ATS) is authoritative. Track B (WebSearch) is discovery-only. If a WebSearch result smells stale or wrong, drop it rather than include it.
- **Handle ATS failures gracefully.** A 404 on one company doesn't kill the run. Log it as a warning, move on.
- **Respect rate limits.** The script parallelizes to 8 concurrent requests by default — don't crank this past 16 without confirming the ATSes tolerate it. Don't re-run the script more than once per hour unless you need fresh data for a specific reason.

## When the user scopes down

- "Only show me Tier 1 roles" → filter the merged list before writing the report.
- "Only new roles posted this week" → freshness filter at `< 7 days`.
- "Just give me {company} and {company}" → skip Track B, run Track A with only those two companies.
- "Search for [specific company] roles" → if they're in `company_ats.json`, poll them directly; if not, run WebSearch with `site:{company-domain}/careers` as a fallback.

## Adding a new company to the target list

When the user says "add {company} to my targets":

1. Append a new entry to `knowledge/company_ats.json`:
   ```json
   {"slug": "newco", "display": "NewCo", "tier": 1, "ats": null, "board_id": "newco", "confidence": "guess"}
   ```
2. Run `discover.py` — it will auto-probe and update the entry when it finds the right ATS.
3. Next run will include NewCo's jobs in the output.

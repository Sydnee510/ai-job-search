# Output Path Conventions

> **Applies to every `ai-job-*` skill that writes a file under `output/`.** Each skill's `SKILL.md` references this file. When a skill writes an artifact, it follows the rule below — no exceptions.

## The rule

All generated files live under a date folder, and per-company artifacts live under a company subfolder inside that date folder. This way, everything generated on a given day is co-located, and everything for a given company on that day sits in one place.

```
output/
  tracker.csv                          # cumulative, project-level (NOT inside a date folder)
  {YYYY-MM-DD}/                        # one folder per day a skill ran
    discover.md                        # cross-company discovery report (no company subfolder)
    _discover_raw.json                 # raw ATS poll data for that day
    {company_slug}/                    # one subfolder per company touched that day
      {company_slug}_{role_slug}_resume.md
      {company_slug}_{role_slug}_resume.pdf
      {company_slug}_{role_slug}_cover.md
      {company_slug}_{role_slug}_cover.pdf
      {company_slug}_{role_slug}_interview_brief.md
      {company_slug}_{role_slug}_jd.md       # if the JD was saved
```

## Worked example

If `ai-job-apply` runs on 2026-04-16 for the Anthropic AI Engineer role, the package goes to:

```
output/2026-04-16/anthropic/anthropic_ai-engineer_resume.pdf
output/2026-04-16/anthropic/anthropic_ai-engineer_cover.pdf
```

If on the same day, `ai-job-apply` also runs for Anthropic People Products:

```
output/2026-04-16/anthropic/anthropic_em-people-products_resume.pdf
output/2026-04-16/anthropic/anthropic_em-people-products_cover.pdf
```

If `ai-job-discover` runs on the same day:

```
output/2026-04-16/discover.md
output/2026-04-16/_discover_raw.json
```

## What stays at the project root (NOT in a date folder)

- `output/tracker.csv` — cumulative across all days. The tracker is the source of truth for pipeline state and must remain at one stable path.

## File formats: which to keep

For each tailored artifact, the renderer produces:

- **`.pdf`** — recruiter-facing. The file actually uploaded to ATSes. Always written.
- **`.md`** — editable source. Edit the `.md` and re-run the renderer to update the PDF without re-tailoring from scratch. Always written.
- **`.html`** — debug-only intermediate (the templated HTML Chrome prints from). NOT written by default. Pass `--keep-html` to `render_pdf.py` if you need to inspect template/font/spacing issues. Can always be regenerated from the `.md`.

## Filenames keep the company prefix even inside a company folder

Yes, the filename `anthropic_ai-engineer_resume.pdf` repeats "anthropic" already present in the folder name. This is intentional: when a recruiter downloads the file (detached from the folder), the filename still identifies the company and role. Don't shorten to `ai-engineer_resume.pdf` inside the folder.

## How skills should construct the path

Pseudocode for any skill writing an artifact:

```
date_dir   = f"output/{today_iso_date}"           # e.g. output/2026-04-16
company_dir = f"{date_dir}/{company_slug}"        # e.g. output/2026-04-16/anthropic
file_path  = f"{company_dir}/{company_slug}_{role_slug}_{kind}.{ext}"
```

Create the directory tree if it doesn't exist (e.g. `mkdir -p` or `Path(...).mkdir(parents=True, exist_ok=True)`).

For cross-company artifacts (discovery), skip the company segment:

```
file_path = f"output/{today_iso_date}/discover.md"
```

## Slug rules

- `company_slug`: lowercase, hyphens, no punctuation. Examples: `anthropic`, `eleven-labs`, `horizon3`.
- `role_slug`: short role identifier, hyphenated. Examples: `em-applied-ai`, `em-remote`, `sem-integrations-apis`.
- Date format: ISO 8601 short form `YYYY-MM-DD`. Always use today's date when the skill runs (not the JD posting date).

## Why this convention exists

Strategically organized output. A user opening `output/` in a finder sees a clean list of dates. Opening any date shows what was worked on that day. Opening a company shows the full application package. No flat directory of 200 mixed files.

## Migration note

Files generated before this convention was introduced may sit at `output/{company_slug}_{role_slug}_*.{ext}`. They're left in place unless explicitly reorganized. New writes always follow the new convention.

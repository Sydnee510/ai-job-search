---
name: ai-job-apply
description: Turn a job description into a tailored application package for any role the user is targeting (AI Engineer, PM, UX Designer, Software Engineer, TPM, Cybersecurity Analyst, etc.). Ingests a JD (URL, pasted text, tracker row ID, or company name from tracker) and produces a fit score, a tailored resume (PDF + markdown), a cover letter (PDF + markdown), and a tracker row. All outputs are drafts for human review. Never auto-submits. For interview prep use ai-job-interview-prep. For pipeline review or follow-ups use ai-job-pipeline.
when_to_use: |
  Triggers: "help me apply to this role", "tailor my resume for this job",
  "draft a cover letter for [company]", "analyze this job description",
  "apply to row N from my tracker", or any message containing a JD URL or
  pasted JD text that mentions a role matching the user's target_job_titles
  in user_profile.json.
allowed-tools: WebFetch Read Write Edit Bash(python3 *)
argument-hint: [jd-url | row-id | company-name]
effort: high
---

# ai-job-apply

**Job-to-be-done:** take one job description in, produce one application package out (analysis + fit score + tailored resume + cover letter + tracker row). This skill runs every time the user applies to a role.

## User profile (auto-injected at skill load)

```!
cat knowledge/user_profile.json
```

The block above is the user's canonical profile. Use it as the source of truth for name, contact, target job titles, career stage, location preferences, and current-employer context. Do NOT hardcode any of these values.

## Skill input

The user invoked this skill with: `$ARGUMENTS`

Resolve the input per the rules below (URL → fetch with WebFetch, pasted text → use verbatim, row ID like `3` or `id 3` → look up the URL via `tracker.py list`, company name → match by company name in tracker). If `$ARGUMENTS` is empty, ask the user for the JD source before proceeding.

## When this skill applies

Triggers:
- "Help me apply to this role: [URL or pasted JD]"
- "Tailor my resume for this job"
- "Draft a cover letter for [company]"
- "Analyze this job description"
- Any message with a JD URL or pasted JD text that mentions a role matching one of `user.targeting.target_job_titles` or `user.targeting.target_job_families`

**NOT this skill:**
- "Prep me for my interview with X" → use `ai-job-interview-prep`
- "Show me my pipeline" / "who should I follow up with" → use `ai-job-pipeline`
- "Submit my approved application" → use `ai-job-submit`

## Inputs

Before running, confirm or elicit:
1. **JD source** — exactly one of:
   - **URL** — fetch with WebFetch
   - **Pasted text** — use verbatim
   - **Tracker row ID** (e.g. "apply to row 3", "apply to id 7") — resolve via `python3 .claude/skills/ai-job-pipeline/tracker.py list` and use the row's `url` field as the JD source. Fail with a clear error if the id doesn't exist.
   - **Company name from tracker** (e.g. "apply to the Acme role from my tracker") — same resolution, but match by company name. If multiple rows match, list them with ids and ask which one.
2. **Company name** — if not obvious from the JD or the tracker row.
3. **Optional:** recruiter context, warm intro, anything unusual about how this application came up.

If missing, ask once then proceed.

### Batch mode

If the user says "apply to rows 3, 7, 9" or "apply to the top 3 in my tracker", run the full pipeline (steps 1–6) once per row in order. Report back per-row outcomes (fit score, output path, any flagged issues) before moving to the next. Stop the batch and ask if any individual fit drops below 6.

## Shared knowledge this skill reads

- `knowledge/user_profile.json` — contact info, target titles, career stage, locations. Auto-injected above.
- `knowledge/master_resume.md` — source of truth for resume content + stage-adaptive bullet variants
- `knowledge/story_bank.md` — STAR stories, only source for cover letter narratives
- `knowledge/target_companies.md` — tier + warmth + notes (for per-company hook context)
- `knowledge/output_conventions.md` — required path layout for every artifact this skill writes (`output/{YYYY-MM-DD}/{company_slug}/...`)
- `knowledge/writing_voice.md` — voice rules (no em-dashes, banned phrases) applied to every artifact
- `knowledge/templates/resume.html` — styled HTML template used for PDF output
- `knowledge/templates/cover_letter.html` — styled HTML template for cover letter PDFs

## Skill-internal assets

- `jd_analysis_rubric.md` — how to extract JD signals
- `positioning_rubric.md` — career-stage bullet selection, IC vs manager framing, summary line templates
- `cover_letter_template.md` — hook formula, banned phrases, worked example
- `render_pdf.py` — renders a tailored markdown file to a styled PDF via Chrome headless

## Pipeline (run in order)

### Step 1 — Ingest

- If URL: `WebFetch` with: "Extract the full job description, company name, team details, requirements, responsibilities, and compensation range."
- If pasted: use verbatim.
- Hold the raw JD in memory. Do not write it to disk.

### Step 2 — Analyze

Apply `jd_analysis_rubric.md`. Output the structured markdown block defined in the rubric. Show it to the user before continuing.

### Step 3 — Score fit (1–10 each)

Produce the scoring table:

| Dimension | Score | Reasoning |
|---|---|---|
| Technical fit | /10 | ... |
| Seniority / scope fit | /10 | ... |
| Compensation likely match | /10 | ... |
| Remote/location | /10 | ... |
| Stage fit | /10 | ... |
| **Overall** | /10 | ... |

**If overall < 6:** stop and ask: "Fit is {X}/10 because {reason}. Proceed anyway, or skip?" Do not tailor further without explicit go-ahead.

### Step 4 — Tailor resume

Apply `positioning_rubric.md` against `knowledge/master_resume.md`:

1. Pick the **stage-adaptive bullet variant** (early / growth / enterprise) matching the JD's detected company stage.
2. Reorder sections so the most relevant signals surface first.
3. Rewrite the summary line to mirror the JD's language — only if honest.
4. Inject JD keywords into bullets ONLY where they already apply. No keyword stuffing.
5. Write the tailored resume as a structured markdown file, following the format the renderer expects (see "Resume markdown format" below).
6. Save to: `output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_resume.md` per `knowledge/output_conventions.md`. Create the date and company directories if they don't exist (`mkdir -p` before the write).
7. Generate the PDF:

   ```bash
   python3 .claude/skills/ai-job-apply/render_pdf.py resume \
     --input output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_resume.md \
     --pdf   output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_resume.pdf
   ```

   This produces the PDF (recruiter-facing). The intermediate `.html` is NOT written by default — pass `--keep-html` to `render_pdf.py` if you need to inspect it for debugging template/font issues. If Chrome isn't installed, the script prints a clear error — fall back to saving only the `.md` and note this to the user.

### Resume markdown format (required structure)

The renderer parses by convention. Follow exactly:

```markdown
# {Full name from user_profile.contact.name}
{contact line: email | phone | linkedin [| github]}

## Professional Summary

{one paragraph, tailored to this JD}

## Work Experience

### {Company} — {Location}
**{Role title}** · {date range}

- Bullet 1
- Bullet 2

### {Next company} — {Location}
**{Role title}** · {date range}

- Bullet 1

## Technical Projects

### {Project name}: {optional one-line tagline}
*{optional subtitle: repo link, project tag}*

- Bullet 1

## Volunteer Community Involvement

### {Org}: {Role} · {dates}
- Bullet 1

## Skills

- **{Category}:** {comma-separated items}
- **{Category}:** ...

## Education

- **{Institution}:** {program}
```

Section headers MUST be exactly: `Professional Summary`, `Work Experience`, `Technical Projects`, `Volunteer Community Involvement`, `Skills`, `Education`. The renderer matches on these names. Omit any section that doesn't apply to a specific tailoring by leaving it empty.

**Em-dash rule for the renderer:** The em-dash in `### {Company} — {Location}` is a structural parser separator. The renderer splits on it and places company left / location right in a flexbox row. The em-dash itself NEVER appears in the rendered PDF for that line. For project and volunteer titles, use colons instead (they ARE visible in output). See `knowledge/writing_voice.md`.

### Step 5 — Draft cover letter

Apply `cover_letter_template.md` + `knowledge/story_bank.md`:

1. Select **ONE story** from the story bank that maps to the JD's #1 requirement. If multiple fit, pick the strongest quantitative outcome.
2. **For AI-native or AI-forward roles, the lead story MUST be an AI-anchored story from the story bank** (typically Story 1 — 0→1 AI system ship — or one of the technical AI projects the user lists in master_resume.md). Never lead with a non-AI story for AI roles.
3. Use the hook formula from `cover_letter_template.md` verbatim — do not deviate.
4. Structure: hook → story (STAR compressed to prose) → why this company specifically → close.
5. Word budget: 250–300. Cut if over.
6. Enforce the banned-phrase list in `cover_letter_template.md`.
7. Save the body (just the 4 paragraphs, no header, no salutation, no signoff) to: `output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_cover.md` per `knowledge/output_conventions.md`. Create the date and company directories if they don't exist.
8. Generate the PDF:

   ```bash
   python3 .claude/skills/ai-job-apply/render_pdf.py cover-letter \
     --body       output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_cover.md \
     --company    "{Company Name}" \
     --salutation "Dear {Hiring Team or named person}," \
     --pdf        output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_cover.pdf
   ```

   The `--date` flag defaults to today. `--name` and `--contact` default to the values in `knowledge/user_profile.json` (contact.name + assembled email|phone|linkedin[|github] line). Override only if writing on behalf of someone else.

### Step 6 — Log tracker row

Append a row to `output/tracker.csv` via the pipeline skill's CLI:

```bash
python3 .claude/skills/ai-job-pipeline/tracker.py add \
  --company "{company}" \
  --role "{role}" \
  --url "{jd_url}" \
  --fit {overall_score} \
  --stage applied \
  --next "follow up in 5 business days" \
  --notes "{one-line summary}"
```

If CSV doesn't exist yet, the script creates it with headers.

## Critical behaviors

- **Output paths are non-negotiable.** Every artifact writes to `output/{YYYY-MM-DD}/{company_slug}/...` per `knowledge/output_conventions.md`. The tracker is the only file that stays at `output/tracker.csv`. Create directories with `mkdir -p` before writing.
- **Voice rules first.** Before writing any resume, cover letter, or summary line, re-read `knowledge/writing_voice.md`. The no-em-dash rule is non-negotiable. Run the self-check at the bottom of that file before saving any output.
- **Never auto-submit.** Outputs are drafts for review. No API calls to job boards. No email sends. That's `ai-job-submit`'s future scope, with human-in-loop required.
- **Ask before fabricating.** If the JD requires something not in the user's story bank, flag it honestly: "JD asks for X, which isn't in your story bank. Options: (a) skip, (b) real story that proves X, (c) reframe existing. What do you want?"
- **Preserve their voice.** Dense, metric-heavy bullets. Active verbs. Keep every number the user put in `master_resume.md`.
- **Call out weak fits.** Overall fit < 6 → stop and ask.
- **Treat the story bank as truth.** Don't invent stories.
- **Years-of-experience honesty.** If a JD requires "N+ years" and the user's `user_profile.career.years_experience` is below it, pause and flag it — don't quietly stretch the number.
- **Leadership claim honesty.** If the JD requires formal people-management experience and `user_profile.career.is_people_manager` is `false`, the skill must NOT claim the user "managed a team of N." Reframe honestly via `positioning_rubric.md` (technical lead, cross-functional lead, mentorship) and flag the JD requirement as a stretch in the fit score.

## Slug conventions

See `knowledge/output_conventions.md` for full path layout. Quick reference:

- `company_slug`: lowercase, hyphens, no punctuation (e.g. "anthropic", "eleven-labs")
- `role_slug`: short role name, hyphenated (e.g. "ai-engineer", "senior-ml-engineer")
- Date folder: `YYYY-MM-DD` (today's date when the skill runs, not the JD posting date)

## When the user scopes down

If the user says "just analyze this JD" — run steps 1–3 only and still append a tracker row with `--stage analyzing`. Nothing gets lost.

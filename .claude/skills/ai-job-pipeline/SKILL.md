---
name: ai-job-pipeline
description: Review, summarize, and act on the user's job-search pipeline state. Reads output/tracker.csv via the tracker.py CLI. Produces a pipeline summary, flags stale applications, and recommends next actions. Does NOT create new applications (that is ai-job-apply) or interview briefs (that is ai-job-interview-prep).
when_to_use: |
  Triggers: "show me my pipeline", "what should I follow up on", "who's stale",
  "where am I in my search", "run my weekly review", "update the tracker for [company]",
  or any aggregate question about applications across multiple rows.
allowed-tools: Read Bash(python3 *)
argument-hint: [optional-filter-or-command]
---

# ai-job-pipeline

**Job-to-be-done:** look at the state of all your applications in one place, decide what to do next. Runs weekly-ish, or any time the user asks a pipeline-level question.

## User profile (auto-injected at skill load)

```!
cat knowledge/user_profile.json
```

## Live pipeline state (auto-injected at skill load)

```!
python3 .claude/skills/ai-job-pipeline/tracker.py list
```

The block above is the live tracker as of this skill invocation. Use it directly. Only re-run the CLI if the user requests a refresh after making changes.

## Skill input

The user invoked this skill with: `$ARGUMENTS`

If empty, run the default pipeline summary. If the input matches a sub-command keyword (`stale`, `weekly`, `update`, `follow up`, etc.), route to the corresponding section below.

## When this skill applies

Triggers:
- "Show me my pipeline"
- "What should I follow up on"
- "Who's stale / who haven't I heard back from"
- "Where am I in my search"
- "Run my weekly review"
- "How many apps am I in on"
- "Update the tracker for [company]"
- Any aggregate question about applications

**NOT this skill:**
- "Help me apply to [role]" → use `ai-job-apply`
- "Prep me for [company] interview" → use `ai-job-interview-prep`
- "Submit my approved app" → use `ai-job-submit`

## Shared knowledge this skill reads

- `knowledge/target_companies.md` — reconcile the tracker against the intended target list (flag high-priority targets not yet applied to)

## Skill-internal assets

- `tracker.py` — CSV CLI (add / list / update). Source of truth for pipeline state. Writes to `output/tracker.csv` at project root.

## Pipeline (pick the subset that matches the user's question)

### Pipeline summary (default when user says "show me my pipeline")

1. Run `python3 .claude/skills/ai-job-pipeline/tracker.py list`
2. Produce a summary:
   - **By stage:** how many in each of {analyzing, drafting, applied, screening, interviewing, offer, rejected, withdrawn, on_hold}
   - **Top 5 by fit score** still active (not rejected / withdrawn)
   - **Stale applications** — applied > 5 business days ago, still in `applied` stage, not yet moved to `screening`
   - **Upcoming actions** — any `next_action` dated within the next 7 days

3. Recommend 3 concrete next actions (specific row ids, specific verbs): "Follow up with Anthropic (id 3), refresh tailored resume for Perplexity (id 7, fit 9/10 but never submitted), pick 3 new Tier 1 targets from `knowledge/target_companies.md`."

### Stale check

- `python3 .claude/skills/ai-job-pipeline/tracker.py list --stage applied`
- Filter for rows where `date` is > 5 business days old and `stage == applied`
- Recommend a follow-up action per stale row

### Update a row

If the user says "update [company] — recruiter reached out" or similar:
1. Find the row via `list --company "[partial]"`
2. Run `tracker.py update --id {n} --stage screening --next "{new_action}" --notes "append: {context}"`
3. Confirm back: "Updated row {n}: {company} now at {stage}, next: {action}"

### Weekly review (when user says "run my weekly review")

This is the orchestrated mode that combines pipeline state with fresh discovery. Run all six steps in order — do not skip the discover step, since the whole point of the weekly is "what should I do this week" and that requires knowing what's new.

1. **Pipeline summary** (the default summary block above).
2. **Conversion check:** applications this week / interviews this week / offers this week.
3. **Gap-to-goal check:** target is 8–12 applications/week — are you on pace?
4. **Discover NEW roles since last week.** Chain `ai-job-discover` with `--since` set to one week before today (or the date of the last weekly review if the user mentions it). Use the ISO date format and write to today's date folder per `knowledge/output_conventions.md`:

   ```bash
   python3 .claude/skills/ai-job-discover/discover.py \
     --output output/{today YYYY-MM-DD}/_discover_raw.json \
     --since {one-week-ago YYYY-MM-DD} \
     --pretty
   ```

   Read the resulting JSON. Surface only NEW roles (cross-reference against `output/tracker.csv` URLs to skip ones you already have rows for). Show the top 5 by score with a one-line reason each. Optionally add them to the tracker as `stage=analyzing` if the user wants.

5. **Target list reconciliation:** which Tier 1 / Tier 2 companies from `knowledge/target_companies.md` haven't been applied to yet? Recommend 3–5 to add to this week's batch.
6. **Story-bank gaps revisited:** did any recent interview flag a `GAP:` that's worth drafting a story for now?

**Combined report** at the end: pipeline state on top, then "what's new this week" from step 4, then "what to do this week" from steps 5–6. The user should be able to read this single report and know exactly which 3–5 actions to take.

## Critical behaviors

- **Voice rules apply.** Pipeline summaries are user-facing artifacts. Re-read `knowledge/writing_voice.md` before writing the summary. No em-dashes, no AI-tell phrases, no corporate-fluff adjectives. Short, specific, numbered.
- **Read-only unless asked.** Don't mutate the tracker unless the user explicitly requests a status change.
- **Confirm destructive updates.** If the user says "mark [company] as rejected", confirm the row before running the update command.
- **Cite the row id.** Every mention of an application should include its `id` so the user can take further action.
- **Don't re-tailor resumes here.** If the weekly review surfaces that an application needs re-tailoring, recommend running `ai-job-apply` — don't silently do it in this skill.
- **Be honest about pacing.** If the user is behind on their target, say so. 3 applications a week isn't 10.

## Output format

A concise markdown report. No fluff. Example shape:

```markdown
# Pipeline — {today's date}

**Totals:** {n} active, {n} applied, {n} screening, {n} interviewing, {n} offer, {n} rejected

## Top 5 active by fit
| id | company | role | fit | stage | next |
|----|---------|------|-----|-------|------|
| ... | ... | ... | ... | ... | ... |

## Stale (applied >5 business days, no movement)
- id 3 — Anthropic, EM Applied AI (applied 04-08) — suggest: follow up via {recruiter or cold email}
- ...

## Recommended actions this week
1. ...
2. ...
3. ...

## Pacing
Target: 8–12 applications/week. This week: {n}. {On pace / X short}.
```

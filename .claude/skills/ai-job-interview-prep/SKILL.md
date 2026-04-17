---
name: ai-job-interview-prep
description: Generate a one-page interview brief for a scheduled interview (any role — AI Engineer, PM, UX Designer, SWE, TPM, Security Analyst, etc.). Different from ai-job-apply. This skill runs AFTER a recruiter screen or round is scheduled, when the user knows the interview format and panel. Produces 5 likely questions with story mappings, 3 smart questions to ask back, explicit GAP flags for missing stories, and a tailored 30/60/90 sketch.
when_to_use: |
  Triggers: "prep me for my interview with [company]", "interview prep for [company]",
  "help me prepare for my [company] interview", "I have a screen with [company] tomorrow",
  or any request to prepare materials for an upcoming scheduled interview round.
allowed-tools: WebFetch Read Write Edit Bash(python3 *)
argument-hint: [company-and-role]
effort: high
---

# ai-job-interview-prep

**Job-to-be-done:** you have an interview scheduled. Produce a one-page brief that you'd carry into the room.

## User profile (auto-injected at skill load)

```!
cat knowledge/user_profile.json
```

The profile above shapes question selection (career_stage + target_job_families drive which rubric categories to weight) and tailors the 30/60/90 sketch.

## Skill input

The user invoked this skill with: `$ARGUMENTS`

Resolve the input as the company (and optionally role) for the upcoming interview. If `$ARGUMENTS` matches a row in the tracker, use the tracker row to pull the JD URL automatically. If empty, ask the user for the company before proceeding.

## When this skill applies

Triggers:
- "Prep me for my interview with [company]"
- "Interview prep for [company]"
- "Help me prepare for my [company] interview"
- "I have a screen with [company] tomorrow" / "a loop at [company] next week"
- Any message that references a *scheduled* interview with a specific company

**NOT this skill:**
- "Should I apply to this role?" → use `ai-job-apply` (analysis step)
- "Tailor my resume for this" → use `ai-job-apply`
- "Show me my pipeline" → use `ai-job-pipeline`

## Inputs

Before running, confirm or elicit:
1. **Company + role** (required)
2. **Interview type** — recruiter screen / hiring-manager screen / technical / panel / final loop. Each calls for different weighting.
3. **Panelists if known** (titles + names). Adjusts which categories to weight.
4. **Format** (30 / 45 / 60 min, video / in-person, etc.)
5. **Recruiter notes** — anything the recruiter said about what the HM cares about. High-signal if you have it.
6. **JD URL or pasted JD text** — needed to re-analyze what they emphasized.

If any of 1, 2, or 6 are missing, ask once then proceed. Other fields are optional but improve the output.

## Shared knowledge this skill reads

- `knowledge/user_profile.json` — target job families (which question categories apply), career_stage (which seniority of questions), is_people_manager (whether to include people-leadership category)
- `knowledge/story_bank.md` — the ONLY source of stories to reference. If a question has no matching story, flag it as `GAP:` — do NOT invent.
- `knowledge/master_resume.md` — for context on what the user has claimed publicly.
- `knowledge/target_companies.md` — notes on this company's stage, product, known compensation, warmth.

## Skill-internal assets

- `interview_prep_rubric.md` — question bank organized by category with mapping guidance for each question to story bank entries.

## Pipeline

### Step 1 — Re-analyze the JD (briefly)

Quick pass on the JD to extract what THIS company is most likely to probe on:
- AI depth classification (AI-native / AI-forward / AI-curious / traditional)
- Seniority + scope (IC vs lead vs manager vs director)
- Team composition signals
- Stage (seed / growth / enterprise / FAANG)

Don't re-produce the full analysis output. Just note the 2–3 signals that shape question selection.

### Step 2 — Select 5 likely questions

From `interview_prep_rubric.md`, pick exactly 5 questions for this interview. Mix based on `user_profile.targeting.target_job_families` + the JD:

- **1 role-specific technical question** from the category matching the user's target family (AI Engineer → architecture/evals; AI PM → prioritization/metrics; AI Researcher → methodology; AI EM → team/process)
- **1 delivery / execution** question
- **1 AI depth question** (always 2 if AI-native / AI-forward role — mark which one is the anchor)
- **1 strategic / judgment** question
- **1 behavioral / culture** question (include "why this role / why now" if this is a screen; include "why this company" for HM+ rounds)

If `user.career.is_people_manager` is `true` OR the target role is a manager-track role, add **1 people leadership** question and bump the mix to 6 total.

For each question, tailor to the JD signals from Step 1. Don't just copy the rubric — specialize it.

### Step 3 — Map each question to a story

For each question, pull the best match from `knowledge/story_bank.md`:
- Name the story explicitly ("Story 1 — 0→1 AI system ship")
- Include a 1-line reminder of the core metric or outcome
- If no story fits well → `GAP: {reason}` — do NOT invent a story

### Step 4 — Draft 3 smart questions for the user to ask

Tailored to this JD / company. Use the templates in the rubric under "Three smart questions" as starting points, then specialize.

Rule: never generic. "What's the culture like?" is banned. Always reference something from the JD or recent company news.

### Step 5 — Tailored 30/60/90

A short, role-specific sketch of what the user's first 30/60/90 days would look like at this company. 3–5 bullets per phase. Reference the JD's emphasis.

### Step 6 — Flag gaps

List every `GAP:` from Step 3 plus any archetype where the story bank is thin for this company's likely probes. These are what the user should pre-think BEFORE the interview.

### Step 7 — Log tracker update

If this interview is on the tracker, update the row:

```bash
python3 .claude/skills/ai-job-pipeline/tracker.py update \
  --id {row_id} \
  --stage interviewing \
  --next "{interview date/type}" \
  --notes "append: prepped brief {date}"
```

If the company isn't on the tracker yet, add it at `--stage interviewing`.

## Output format

Save to: `output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_interview_brief.md` per `knowledge/output_conventions.md`. Create the date and company directories if they don't exist (`mkdir -p`).

Structure:

```markdown
# Interview Brief — {Company} — {Role}
Format: {type}, {duration}, {panelists}
Prepared: {date}

## Signals from the JD
- {2–3 bullets}

## Likely questions and your stories

1. **[Category]** {question}
   Story: {story name from story_bank.md}
   Core metric: {one line}

2. ...

[5–6 total, depending on whether the role includes people leadership]

## 3 smart questions to ask them
1. {question} — {why this one for this company}
2. ...
3. ...

## Your 30/60/90 sketch
**30 days:** ...
**60 days:** ...
**90 days:** ...

## Gaps to pre-think
- GAP: {question where no strong story exists — what to figure out before the interview}
- ...

## Close
Always end with: "Is there any concern about my fit that I can address right now before we wrap?"
```

## Critical behaviors

- **Voice rules first.** Before writing the brief, re-read `knowledge/writing_voice.md`. No em-dashes in any generated text. No banned AI-tell phrases. Run the self-check before saving.
- **Never invent a story.** If the story bank doesn't cover a likely question, flag it. Don't paper over.
- **Be specific to this company.** A generic interview brief is worse than no brief. Reference the JD, the product, recent launches.
- **Call out "why this role" preparation explicitly.** The most common question at a first-round screen is the "why this role / why now" version. The brief should remind the user of their working draft from `story_bank.md` Story 10 and the `leaving_reason_short` in `user_profile.json`.
- **Do not regenerate the resume or cover letter.** Those are `ai-job-apply`'s job. Interview prep assumes the application package is already drafted.

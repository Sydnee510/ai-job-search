---
name: ai-job-submit
description: Submit an already-reviewed application package to a specific ATS or company form. Currently a STUB, not yet implemented. On invocation, this skill explains the current manual submission flow and asks the user to implement the ATS-specific handler they need (Greenhouse, Lever, Ashby, Workday, LinkedIn Easy Apply, custom company form, or email to recruiter). Intentionally human-in-the-loop. This skill will never auto-submit without explicit per-application user confirmation.
when_to_use: |
  Triggers: "submit my approved application to [company]", "send the [company] application",
  "apply to [company] now". User-invoke only (disable-model-invocation is true), so Claude
  will not auto-load this skill.
disable-model-invocation: true
argument-hint: [company-slug]
---

# ai-job-submit (STUB)

**Status:** intentionally not implemented. This SKILL.md documents the safety boundary and the intended design so future implementation can slot in cleanly.

## User profile (auto-injected at skill load)

```!
cat knowledge/user_profile.json
```

## Skill input

The user invoked this skill with: `$ARGUMENTS`

This is the company slug (or company name) for the application package to surface for manual submission. Look up the package under `output/{YYYY-MM-DD}/{company_slug}/` per `knowledge/output_conventions.md`.

## Why this skill isn't implemented yet

Job application submission is:

1. **High blast radius.** A bad submission sends a half-formed pitch to a real recruiter. Recovery is awkward.
2. **ATS-specific.** No universal submission API. Every target system (Greenhouse, Lever, Ashby, Workday, LinkedIn Easy Apply, custom forms, direct email) needs its own handler.
3. **Applicant-side APIs are rare.** Greenhouse / Lever / Ashby have APIs for employers, not applicants. LinkedIn doesn't expose Easy Apply via API. Realistic options are browser automation (Playwright) with human-in-loop, or pre-fill + manual submit.
4. **YAGNI.** The user is pre-5-applications. Until they know which ATS they actually hit most often, building a submit handler is premature.

## When this skill applies

Triggers:
- "Submit my approved application to [company]"
- "Send the [company] application"
- "Apply to [company] now"

On any of these, the skill:
1. Confirms the application package exists in `output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_*.{md,pdf}`
2. Confirms the user has reviewed the drafts (explicit question: "Have you reviewed and approved both the resume and cover letter? Paste any edits before I proceed.")
3. Explains that submission is currently manual: open the JD URL, upload the files, review before clicking submit
4. Updates the tracker with `--stage applied` once the user confirms they've submitted

## Intended future design (when you're ready to build it)

Principles:
- **Human-in-the-loop is non-negotiable.** The skill never clicks "Submit" without the user's explicit confirmation for that specific application.
- **One handler per ATS.** Each handler lives in `handlers/` inside this skill directory (e.g., `handlers/greenhouse.py`, `handlers/lever.py`, `handlers/linkedin_easy_apply.py`).
- **Handlers are pre-fill, not auto-submit.** They navigate the form, upload files, fill fields, and stop at the review step. User reviews and clicks submit themselves.
- **Detection layer.** Given a JD URL, detect which ATS it's on (URL pattern match: `boards.greenhouse.io`, `jobs.lever.co`, `job-boards.ashbyhq.com`, etc.) and route to the right handler.

Proposed structure when implemented:

```
ai-job-submit/
├── SKILL.md
├── detect.py           # URL → ATS name
├── handlers/
│   ├── greenhouse.py   # Playwright script, stops at review
│   ├── lever.py
│   ├── ashby.py
│   ├── workday.py
│   ├── linkedin_easy_apply.py
│   └── email_recruiter.py   # Drafts email, doesn't send
└── tests/              # integration tests with recorded DOMs
```

## What to do when the user triggers this skill today

Since this is still a stub, respond with:

> **ai-job-submit is not implemented yet.** Current manual flow:
>
> 1. Open the JD URL in your browser.
> 2. Upload `output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_resume.pdf` and `output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_cover.pdf`.
> 3. Review everything once more. Check the cover letter company name matches. Check the resume summary matches the role.
> 4. Submit.
> 5. Come back here and say "update tracker for {company} — submitted". The ai-job-pipeline skill will move the row to `applied`.
>
> When you've submitted 5+ applications, we can implement this skill with a real Playwright handler for whichever ATS you hit most often.

## Critical behavior (applies even as a stub)

- **Voice rules apply** to any recruiter email drafts or status messages this skill generates. Re-read `knowledge/writing_voice.md` first. No em-dashes, no AI-tell phrases.
- **Never claim to have submitted anything.** If the user asks "did you submit it?", the answer is always: "No. I don't auto-submit. Did you submit it manually?"
- **Always verify review.** Before even suggesting submission is ready, confirm the user has reviewed the drafts in the company's date folder under `output/{YYYY-MM-DD}/{company_slug}/` per `knowledge/output_conventions.md`.

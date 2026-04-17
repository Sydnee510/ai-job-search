# Example output

> **Fictional example.** This folder is a captured end-to-end run of the four core skills (discover, apply, interview-prep, pipeline) for a fictional candidate, **Jordan Taylor Chen**, applying to real open Anthropic / Scale AI / Cohere roles as of 2026-04-17.
>
> Nothing in here was actually submitted. The candidate doesn't exist. The ATS URLs were real at capture time (they may or may not still be live when you read this). All tracker entries are illustrative.

## Why this folder exists

To show forkers what the skills actually produce before they've run anything. If you're evaluating whether this toolkit will give you drafts you'd be willing to send, read the files below as a preview.

## Contents

```
example-output/
├── tracker.csv                    ← 4 illustrative rows across different stages
└── 2026-04-17/
    ├── _discover_raw.json        ← raw ATS poll data from a live discover.py run
    ├── discover.md               ← ranked markdown report (ai-job-discover output)
    ├── pipeline_summary.md       ← weekly-review-style summary (ai-job-pipeline output)
    └── anthropic/
        ├── anthropic_applied-ai-eng_resume.md     ← tailored resume markdown
        ├── anthropic_applied-ai-eng_resume.pdf    ← rendered PDF (blue brand)
        ├── anthropic_applied-ai-eng_cover.md      ← tailored cover letter markdown
        ├── anthropic_applied-ai-eng_cover.pdf     ← rendered PDF
        └── anthropic_applied-ai-eng_interview_brief.md  ← one-page brief with GAP flags
```

## Flow this captures

1. **discover** ran live against `knowledge/company_ats.json` (12 companies). Results in `_discover_raw.json`, summarized in `discover.md`. 21 roles matched Jordan's `target_job_titles`, top 9 new ones surfaced.
2. **apply** was triggered on the #2 role (Anthropic: Applied AI Engineer, Beneficial Deployments). Produced the tailored resume + cover letter + tracker row 1.
3. **interview-prep** was triggered after a screen was scheduled. Produced the interview brief with 5 likely questions mapped to story slots, 3 smart questions to ask back, a 30/60/90 sketch, and 3 explicit GAP flags.
4. **pipeline** ran a weekly review. Produced `pipeline_summary.md` with totals by stage, stale flags, and 3 concrete actions.

## What's NOT in this example

- `ai-job-submit` has no output folder because the skill is intentionally a stub (humans click Submit).
- No custom `user_profile.json` — Jordan Chen's contact info was passed as `--name` / `--contact` overrides to `render_pdf.py` for this demo so the real template `user_profile.json` stays untouched.
- Follow-up iterations. Real use would show stage progressions (applied → screening → interviewing → offer/rejected) over weeks. This is a single snapshot.

## If you want to regenerate your own version

Edit `knowledge/user_profile.json` with your details, then run:

```bash
# 1. Discover
python3 .claude/skills/ai-job-discover/discover.py --pretty \
  --output output/$(date +%Y-%m-%d)/_discover_raw.json

# 2. Apply (via Claude Code: "help me apply to [url]")
# 3. Interview prep (via Claude Code: "prep me for my [company] interview")
# 4. Pipeline (via Claude Code: "show me my pipeline")
```

Your own `output/` is gitignored. This `example-output/` folder stays in the repo as a reference.

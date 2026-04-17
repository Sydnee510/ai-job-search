<div align="center">

# ai-job-search

### A Claude Code skill system that runs your job search end-to-end.

[![Python](https://img.shields.io/badge/Python-3.9+-1E40AF?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a1a)](https://www.python.org/)
[![Claude Code](https://img.shields.io/badge/CLAUDE_CODE-Skills-1E40AF?style=for-the-badge&logo=anthropic&logoColor=white&labelColor=1a1a1a)](https://claude.com/claude-code)
[![Chrome](https://img.shields.io/badge/Chrome-Headless_PDF-1E40AF?style=for-the-badge&logo=googlechrome&logoColor=white&labelColor=1a1a1a)](https://www.google.com/chrome/)
[![Greenhouse](https://img.shields.io/badge/Greenhouse-ATS-1E40AF?style=for-the-badge&labelColor=1a1a1a)](https://www.greenhouse.io/)
[![Lever](https://img.shields.io/badge/Lever-ATS-1E40AF?style=for-the-badge&labelColor=1a1a1a)](https://www.lever.co/)
[![Ashby](https://img.shields.io/badge/Ashby-ATS-1E40AF?style=for-the-badge&labelColor=1a1a1a)](https://www.ashbyhq.com/)

### No recruiter. No network. No problem.

Five specialized skills: **discover** open roles, **apply** with tailored resume + cover letter PDFs, **interview-prep** one-page briefs, **pipeline** review, **submit** safeguards. Every skill is one job-to-be-done. Fork it, fill in `knowledge/user_profile.json` with your info, run the same system.

**Works for any role** — AI Engineer, Product Manager, UX Designer, Software Engineer, Technical Program Manager, Cybersecurity Analyst, Data Scientist, Developer Advocate, Researcher, Designer, or anything else. The default examples lean AI; the system is role-agnostic. See [knowledge/user_profile_schema.md](knowledge/user_profile_schema.md) for starter title lists per role family.

</div>

---

## What it does

Five peer skills, one per job-to-be-done:

| Skill | When to invoke | What you get |
|---|---|---|
| **ai-job-discover** | "Find me open roles" | Ranked list of fresh postings matching your `target_job_titles` from Greenhouse/Lever/Ashby + WebSearch, tracker rows created |
| **ai-job-apply** | "Help me apply to this role [URL]" | JD analysis, fit score, tailored resume PDF, cover letter PDF, tracker row |
| **ai-job-interview-prep** | "Prep me for my interview with X" | One-page brief with likely questions, story mappings, smart questions to ask, 30/60/90 sketch |
| **ai-job-pipeline** | "Show me my pipeline" / "weekly review" | Summary, stale flags, pacing check, recommended next actions |
| **ai-job-submit** | "Submit my approved app to X" | (Stub. Submission is manual by design.) |

Together they turn the application funnel into a single command: **discover → apply → interview-prep → pipeline review**, with submission as the one human-only step.

Visual workflow diagrams: [docs/workflows.html](docs/workflows.html)

---

## What makes it different

- **No fluff in output.** Enforced "no em-dash" rule + banned AI-tell phrase list, applied to every generated artifact. Drafts don't read like ChatGPT wrote them.
- **Grade-A PDFs.** HTML-templated resume + cover letter in a clean deep-blue brand (Times New Roman, gold-accent variant available — swap one hex to recolor). Rendered via Chrome headless. Zero new installs needed on macOS.
- **Stage-adaptive positioning.** Every bullet in `master_resume.md` can maintain 3 variants (early / growth / enterprise). The skill picks based on JD stage detection, not a one-size-fits-all tailoring.
- **Story-bank discipline.** Cover letters and interview briefs pull from a single STAR story bank. If no story fits, the skill flags it as a `GAP:`. It won't invent stories to paper over weakness.
- **Direct-ATS discovery.** Polls Greenhouse/Lever/Ashby public APIs for your target companies. Auto-probes unknown ATSes and caches corrections. Pairs with WebSearch for stealth/new-company coverage.
- **Role-agnostic.** `target_job_titles` in `user_profile.json` is the single knob. Set it to "Senior AI Engineer" or "UX Designer" or "Cybersecurity Analyst" — the skill adapts.
- **Honest about limits.** `ai-job-submit` is deliberately a stub. Auto-submission is high blast radius with per-ATS complexity. The skill explains the safe manual flow instead.

---

## Project layout

```
ai-job-search/
├── README.md                         ← you are here
├── ROADMAP.md                        ← aspirational next phase
├── .claude/
│   └── skills/
│       ├── ai-job-discover/          ← discover open roles
│       │   ├── SKILL.md
│       │   ├── discover.py
│       │   └── workflow.html         ← visual flow diagram
│       ├── ai-job-apply/             ← JD → tailored resume + cover PDFs
│       │   ├── SKILL.md
│       │   ├── jd_analysis_rubric.md
│       │   ├── positioning_rubric.md
│       │   ├── cover_letter_template.md
│       │   ├── render_pdf.py
│       │   └── workflow.html
│       ├── ai-job-interview-prep/    ← interview brief
│       │   ├── SKILL.md
│       │   ├── interview_prep_rubric.md
│       │   └── workflow.html
│       ├── ai-job-pipeline/          ← pipeline review + tracker
│       │   ├── SKILL.md
│       │   ├── tracker.py
│       │   └── workflow.html
│       └── ai-job-submit/            ← stub (safety boundary)
│           ├── SKILL.md
│           └── workflow.html
├── knowledge/                         ← user-owned, forkable
│   ├── user_profile.json             ← your identity + targeting (EDIT THIS FIRST)
│   ├── user_profile_schema.md        ← field-by-field docs
│   ├── master_resume.md              ← source of truth for resume content
│   ├── story_bank.md                 ← STAR stories (only source for narratives)
│   ├── target_companies.md           ← tiered target list with notes
│   ├── company_ats.json              ← company → ATS mapping for discovery
│   ├── output_conventions.md         ← required output path layout
│   ├── writing_voice.md              ← no-em-dash rule + banned phrases
│   └── templates/
│       ├── resume.html               ← styled HTML template (deep blue #1E40AF)
│       └── cover_letter.html         ← cover letter HTML template
├── docs/
│   └── workflows.html                ← index of all 5 skill workflows
├── example-resume-template/           ← rendered sample PDF + source md
└── output/                            ← generated drafts + tracker.csv (gitignored)
```

---

## Setup (20 minutes, one-time)

### 1. Prerequisites

- **Claude Code:** install from [claude.com/claude-code](https://claude.com/claude-code).
- **Python 3.9+:** macOS ships with this. `python3 --version` to check.
- **Google Chrome:** used for HTML-to-PDF rendering. Default path `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` on macOS. Override with `CHROME` env var or `agent_runtime.chrome_binary` in `user_profile.json`.

Zero Python package installs. All scripts are stdlib-only.

### 2. Clone / fork

```bash
git clone https://github.com/YOUR-USERNAME/ai-job-search ~/ai-job-search
cd ~/ai-job-search
```

Or fork via the GitHub UI and clone your fork.

### 3. Fill in your content (this is where you actually customize)

The whole system reads from a handful of files in `knowledge/`. Edit them in the order below.

| Step | File | What to change | Priority |
|---|---|---|---|
| **3a** | [knowledge/user_profile.json](knowledge/user_profile.json) | `contact.*` (name, email, phone, linkedin, github, location_city); `targeting.target_job_titles` (copy from the `_role_examples` block in the file); `career.*` (stage, years, current role/employer, `is_people_manager`, `direct_reports`); `locations[]` (drop/edit to your cities); `compensation.*`; `agent_runtime.user_agent_contact`. Full field docs in [user_profile_schema.md](knowledge/user_profile_schema.md). | **Critical** |
| **3b** | [knowledge/master_resume.md](knowledge/master_resume.md) | Replace every `[PLACEHOLDER]` bullet with your own. For high-impact bullets, keep the 3-variant pattern (early / growth / enterprise) so the skill can pick based on JD stage. | **High** |
| **3c** | [knowledge/story_bank.md](knowledge/story_bank.md) | Fill in the 10 STAR-story slots. This is the single highest-leverage hour of the whole process. Leave `GAP:` where you don't have a story yet — the skills will flag gaps honestly rather than invent. | **High** |
| **3d** | [knowledge/target_companies.md](knowledge/target_companies.md) | Replace the seeded companies with your target list. Mark warmth + priority per row. Keep the tier structure as a framework. | **Medium** |
| **3e** | [knowledge/company_ats.json](knowledge/company_ats.json) | Add your target companies with their ATS. For new ones you don't know the ATS of, set `"ats": null`. The script auto-probes Greenhouse → Lever → Ashby. | **Medium** |
| **3f** | [knowledge/templates/resume.html](knowledge/templates/resume.html) + [cover_letter.html](knowledge/templates/cover_letter.html) | Change `--brand-accent` hex in the CSS `:root` if you want different brand colors (default is deep blue `#1E40AF`). Change the font stack if you don't want Times New Roman. | Low |
| **3g** | [knowledge/writing_voice.md](knowledge/writing_voice.md) | Adjust banned phrases to your taste. The no-em-dash rule is non-negotiable. | Low |

**If you target non-AI roles**, also edit [.claude/skills/ai-job-discover/discover.py](.claude/skills/ai-job-discover/discover.py):
- `AI_BOOST_PATTERNS` — swap in keywords relevant to your field (e.g. `\bsecurity\b`, `\bdesigner\b`, `\bresearcher\b`).
- `EXCLUDE_PATTERNS` — loosen if any of the defaults collide with your target titles.

### 4. Optional: first smoke test

From the project root:

```bash
# Test the tracker (should print headers only on first run)
python3 .claude/skills/ai-job-pipeline/tracker.py list

# Test the discover script against your seeded target list
python3 .claude/skills/ai-job-discover/discover.py --pretty --output /tmp/discover_test.json

# Test the PDF renderer against the included example resume
python3 .claude/skills/ai-job-apply/render_pdf.py resume \
  --input example-resume-template/example_resume.md \
  --pdf   example-resume-template/example_resume.pdf
```

All three should succeed with no external dependencies. If the PDF renderer fails, Chrome isn't installed or isn't at the expected path — set `CHROME=/path/to/chrome` or `agent_runtime.chrome_binary` in `user_profile.json`.

---

## Daily usage

Open Claude Code in this directory (`cd ~/ai-job-search && claude`) and talk to it in natural language. The skills auto-activate based on what you say.

### Typical flow

```text
you: find me some new roles this week
claude: [runs ai-job-discover]
        → Polled 12 target companies, found 67 roles matching your
          target titles, 12 new. Top 5 are Anthropic Senior AI
          Engineer, Notion Applied AI, OpenAI Platform Engineer, …
          Added 12 rows to tracker.csv at stage=analyzing.

you: help me apply to the Anthropic Senior AI Engineer role
claude: [runs ai-job-apply]
        → Fetches JD, analyzes (AI-native, growth-stage, fit 8.6/10),
          tailors resume, drafts cover letter, saves both PDFs to
          output/. Shows you the drafts.

you: review + approve
[you open the PDFs, make any tweaks to the .md source if needed,
 re-render with render_pdf.py, then submit manually]

you: update pipeline: submitted to anthropic
claude: [runs ai-job-pipeline]
        → Row 7 advanced to stage=applied, next action logged.

[a few days later]
you: prep me for my interview with Anthropic tomorrow
claude: [runs ai-job-interview-prep]
        → Generates one-page brief with 5 likely questions mapped
          to your story bank, 3 smart questions to ask back.

you: show me my pipeline
claude: [runs ai-job-pipeline]
        → {n} applications active, {n} interviewing, 2 stale,
          recommended follow-ups list.
```

### Common invocations

| Say this | Skill triggered |
|---|---|
| "Find me jobs", "what roles are open this week" | ai-job-discover |
| "Help me apply to [URL]", "tailor my resume for this role" | ai-job-apply |
| "Prep me for my [company] interview" | ai-job-interview-prep |
| "Show me my pipeline", "weekly review", "who should I follow up on" | ai-job-pipeline |
| "Submit my approved app to [company]" | ai-job-submit (stub) |

---

## Location + compensation preferences

[`knowledge/user_profile.json`](knowledge/user_profile.json) drives location ranking and comp gates for `ai-job-discover`. The `locations[]` array is ordered by your priority. Defaults in the template:

```
Remote             (+10)   # highest priority
New York, NY       (+7)
San Francisco, CA  (+5, verify >= $200k base)
```

How it works:
- Every role gets its location checked against the `aliases` list (word-boundary match, so `"GA"` doesn't match `"Bangalore"`).
- On match, the location's `weight` is added to the role's overall score. Preferred locations float to the top.
- Locations with `min_base_usd` set (like SF at $200k) get a `⚠ COMP >= $Xk: verify base before applying` tag in the report. ATS APIs rarely include salary, so this is a reminder to check the JD, not a hard filter.

To change your priorities, edit `user_profile.json` and save. The next `ai-job-discover` run picks it up.

---

## Direct script usage (without Claude)

You can run the scripts outside Claude Code too:

```bash
# Discover roles across target companies
python3 .claude/skills/ai-job-discover/discover.py --pretty --output output/roles.json

# Tracker operations
python3 .claude/skills/ai-job-pipeline/tracker.py add \
  --company "Anthropic" --role "Senior AI Engineer" \
  --url "https://..." --fit 8 --stage applied \
  --next "follow up 2026-04-25" --notes "warm intro via X"

python3 .claude/skills/ai-job-pipeline/tracker.py list --stage applied
python3 .claude/skills/ai-job-pipeline/tracker.py list --min-fit 7
python3 .claude/skills/ai-job-pipeline/tracker.py update --id 3 --stage interviewing

# Render a resume markdown to PDF
python3 .claude/skills/ai-job-apply/render_pdf.py resume \
  --input output/2026-04-16/anthropic/anthropic_senior-ai-eng_resume.md \
  --pdf   output/2026-04-16/anthropic/anthropic_senior-ai-eng_resume.pdf

# Render a cover letter (uses name/contact from user_profile.json by default)
python3 .claude/skills/ai-job-apply/render_pdf.py cover-letter \
  --body output/2026-04-16/anthropic/anthropic_senior-ai-eng_cover.md \
  --company "Anthropic" \
  --salutation "Dear Anthropic Team," \
  --pdf output/2026-04-16/anthropic/anthropic_senior-ai-eng_cover.pdf

# Add --keep-html to either subcommand to also persist the intermediate
# .html beside the PDF (useful only when debugging template/font issues).
```

---

## Architecture notes (for the curious)

### Why "job-to-be-done" skill boundaries

Each skill maps to one red-box workflow. You don't split a skill by file type or by step. You split by when the user's *intent* changes. Applying to a role is a different intent than prepping for an interview; they get different skills. See [docs/workflows.html](docs/workflows.html) for the visual.

### Why ai-job-submit is a stub

Submission is the one step where auto-execution has high blast radius (misfire = a half-formed pitch lands in a real recruiter's inbox). Every ATS has different form shapes, and applicant-side APIs barely exist. A real submit handler means Playwright browser automation per ATS (Greenhouse, Lever, Ashby, Workday, LinkedIn Easy Apply) with human-in-loop confirmation before the final click. That's a v2 build to tackle after you've done 5+ manual submissions and know which ATS you hit most often. See [ROADMAP.md](ROADMAP.md).

### Why direct-ATS polling beats LinkedIn scraping

LinkedIn Jobs rendering is JavaScript-heavy, rate-limited, TOS-restricted, and noisy (duplicate recruiter reposts flood the top). Greenhouse/Lever/Ashby public APIs are fresher (5-minute propagation vs. hours/days), authoritative (the company's own ATS), and free. ~80% of AI-native startups and a large share of growth-stage tech companies use one of those three.

### Why shared knowledge/ at project root, not in skills

Skills are *mechanisms*. Knowledge (profile, resume, stories, company list, templates) is *user data* that flows across skills. Putting it in `knowledge/` at the project root makes the fork point explicit: clone the repo, edit the files in `knowledge/`, and the skills work against your data.

### Why Chrome headless for PDFs

- Already installed on every Mac
- Better rendering fidelity than weasyprint on complex CSS
- Zero Python dependencies (stdlib `subprocess` is enough)
- Intermediate `.html` is rendered to a tempdir and discarded by default; pass `--keep-html` if you need to inspect it for debugging

### Why stdlib-only Python

Portability. No `pip install` means no Python environment drift, no `requirements.txt`, no venv setup friction. If you can run `python3`, you can run this.

### Why user_profile.json is injected at skill load

Every `SKILL.md` starts with an auto-injection block that runs `cat knowledge/user_profile.json` at load time. The model sees your identity + targeting without you having to re-state it. Edit the file once, every skill picks it up on the next invocation.

---

## Troubleshooting

### "Chrome / Chromium not found" when rendering PDFs

Either install Chrome or set `CHROME` env var / `agent_runtime.chrome_binary` in `user_profile.json`:

```bash
export CHROME=/path/to/your/chromium
python3 .claude/skills/ai-job-apply/render_pdf.py resume ...
```

### Discover script returns 0 jobs for a company

The `board_id` in `knowledge/company_ats.json` is probably wrong. Visit the company's careers page and check the URL:

- `boards.greenhouse.io/{id}` → set `"ats": "greenhouse", "board_id": "{id}"`
- `jobs.lever.co/{id}` → set `"ats": "lever", "board_id": "{id}"`
- `jobs.ashbyhq.com/{id}` → set `"ats": "ashby", "board_id": "{id}"`

If they use something else (Workday, Personio, custom), set `"ats": null` with `"notes": "Probe disabled: not on Greenhouse/Lever/Ashby"` and the script will skip them. Pick those roles up via WebSearch in `ai-job-discover` Track B.

### Discover returns 0 roles even with the right board_id

Check that `user_profile.targeting.target_job_titles` actually matches the titles the company posts. The filter is word-boundary exact by default. If you target "AI Engineer" but the company posts "Senior AI Systems Engineer", add that to your title list or loosen the pattern.

### Resume PDF has em-dashes where I didn't want them

Check the source `.md` file in `output/{YYYY-MM-DD}/{company_slug}/`. The renderer preserves content verbatim from the markdown. Edit the `.md`, re-run `render_pdf.py resume` against the same paths, re-verify.

### Tracker CSV in a weird place

The tracker defaults to `{project_root}/output/tracker.csv`. Override with `AI_JOB_PROJECT_ROOT=/your/path python3 tracker.py list` if you need a non-default location.

---

## What's next

[ROADMAP.md](ROADMAP.md) sketches the next phase: a supervised-agent weekly flow that wakes on Monday, runs pipeline review, surfaces new roles, and queues tailored drafts for the user to approve. Aspirational only. Read before designing.

---

## Contributing / forking

Fork, swap `knowledge/`, make it yours. PRs that add value across users (new ATS adapter, better title regex, new bundled skill, non-AI-role rubric variants) are welcome. PRs that personalize `knowledge/` for individual forkers are not — fork and keep your own.

High-impact contribution targets:

- **`ai-job-submit` real implementation:** one Playwright handler per ATS (Greenhouse, Lever, Ashby, Workday, LinkedIn Easy Apply). Each handler should stop at the review step; human clicks final submit.
- **HN Who's Hiring parser:** monthly thread. High-signal discovery for stealth/YC companies.
- **Additional ATS adapters:** SmartRecruiters, Workable, Personio, Greenhouse Inbound.
- **Resume DOCX export:** for ATSes that reject PDFs.
- **Role-family rubric packs:** a `positioning_rubric_pm.md`, `positioning_rubric_ux.md`, `positioning_rubric_security.md` set of variants the skill can auto-select based on `target_job_families`.

---

## Attribution

Built in collaboration with Claude Code.

License: MIT. Use it, fork it, improve it.

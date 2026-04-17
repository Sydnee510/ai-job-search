# Roadmap

> **Status: aspirational.** [README.md](README.md) documents what works today. This file documents what we'd build **next**, only after the trigger conditions below are met. Nothing here is a commitment.

---

## North star

A **supervised-agent weekly flow**. On a recurring schedule (Monday morning by default), the system wakes up and:

1. Runs the pipeline review (stale flags, follow-up dates, conversion check).
2. Runs `ai-job-discover --since` to surface roles posted in the last week.
3. Queues tailored draft application packages for any new role above a fit threshold.
4. Pings the user with a review queue (notification surface to be decided).
5. The user approves, rejects, or edits each draft.
6. Approved drafts advance to a `ready_to_submit` tracker stage.
7. The user clicks final Submit manually, on every application, forever.

The agent does the funnel mechanics. The user does the judgment.

---

## Phase comparison

| Aspect | Today (manual command-driven) | Next phase (supervised agent) | Never (full automation) |
|---|---|---|---|
| Discovery | User asks "find me jobs" | Scheduled weekly run | Same |
| JD analysis + tailoring | User asks "apply to row 3" | Auto-queued for new high-fit roles | Same |
| Draft review | User reads PDF in IDE | Batch review queue with approve/reject | Same |
| ATS form fill | Manual upload | Playwright pre-fills, stops at review | Auto-submit |
| Final submit | Human click | Human click | Never built |
| Tracker advance | User says "applied" | User clicks "submitted" in review UI | Auto-advance on submit |

---

## Trigger conditions (do not start building until ALL are true)

- [ ] **20+ manual applications shipped.** We have 3 today. Premature automation when the funnel pattern isn't clear yet.
- [ ] **Recruiter response cadence understood.** Average days from applied to first reply, average conversion rate from applied to screening, by ATS.
- [ ] **Dominant ATS identified.** Top 1 or 2 by application volume. Build the Playwright handler for that one first, not all five at once.
- [ ] **Friction points logged.** Where does the manual flow actually hurt? Form-filling? Custom questions? Tracker bookkeeping? The friction log decides what the agent automates first.

When all four boxes are checked, re-read this file and start designing.

---

## Prerequisites that need a user decision before design

These are blocking decisions. They cannot be defaulted by the engineer. The user has to call them.

| Decision | Why it matters | Default to consider | User input required |
|---|---|---|---|
| Playwright as a Python dep | First non-stdlib dependency in the project. Breaks the "zero installs" promise from the README. | Yes, gated behind `pip install -r .claude/skills/ai-job-submit/requirements.txt` so the rest of the system stays stdlib-only | Approve / deny / suggest alternative (e.g. Selenium, Puppeteer-via-Node) |
| `knowledge/applicant.json` schema | Holds standard demographic + work-auth answers the agent needs to fill ATS forms (name, email, phone, LinkedIn, work authorization, demographic self-id, salary expectation). Sensitive. | Project-local file, gitignored, schema documented in `knowledge/applicant_schema.md` | Confirm structure, decide which fields are optional, decide if the file lives inside the repo or outside |
| Notification surface | How the user finds out the weekly batch is ready for review | Terminal notification + file in `output/{date}/_review_queue.md` | Pick one: terminal-only, macOS notification, Slack DM, email, all of the above |
| Scheduled trigger | What actually fires the weekly run | Claude Code's `/schedule` skill (cron-style triggers) | Confirm `/schedule` is the right mechanism vs. external cron + headless Claude invocation |
| Auto-fill scope | What the agent fills vs. what stays user-only | Agent fills standard fields. Custom per-role questions flagged for the user to write live. | Confirm — or insist agent stops the moment it sees ANY custom question, even simple ones |

---

## Architecture sketch (intentionally vague)

Component names only. Do not over-design before the trigger conditions hit.

- `ai-job-orchestrate/SKILL.md` — top-level state machine that chains the weekly flow. Reads scheduled trigger, calls existing skills, manages a `_review_queue` artifact.
- `knowledge/applicant.json` — source of truth for standard ATS form answers. Gitignored if it holds real PII.
- `ai-job-submit/handlers/` — per-ATS Playwright modules (`greenhouse.py` first, `lever.py` and `ashby.py` next, `workday.py` and `linkedin_easy_apply.py` deferred or never).
- `ai-job-submit/detect.py` — URL pattern match → ATS handler routing.
- `output/{YYYY-MM-DD}/_review_queue.md` — the batch review artifact the user reads on Monday.

Existing skills the orchestrator chains:
- `ai-job-pipeline` (already supports weekly review mode)
- `ai-job-discover` (already supports `--since`)
- `ai-job-apply` (already supports row-ID and batch mode)

So most of the orchestrator's job is already wired. The new work is the Playwright handler, the applicant schema, and the review queue UX.

---

## Open questions to keep on file

These don't need answers now. They need to be on the table when design starts.

1. **Per-role custom questions.** Greenhouse and Lever both let employers add free-form custom questions per JD ("What's your salary expectation?", "Why this team specifically?", "Do you have a portfolio?"). The agent cannot answer these without the user. Options: stop and prompt, skip the role, generate a draft answer for user review.
2. **Batch review UX.** Should the user see all 5 drafts at once as a table, one at a time as a focus mode, or a hybrid?
3. **Abort and rollback.** If the agent pre-fills a Greenhouse form and the user sees garbage, how do they reset cleanly? Close the browser, clear partial state, re-queue?
4. **Double-submit detection.** If the user manually applied to a role last week without telling the tracker, the agent might queue a duplicate this week. How does it detect already-submitted state? Email confirmation parsing? Manual tracker discipline? An "already applied" Bloom filter on URLs?
5. **Drift detection.** If a JD changes after we drafted the application, the cover letter may no longer match. Do we re-fetch the JD before queuing for review? Diff against the cached version?

---

## Hard constraints (these never change)

> **The final Submit click is human-only.** No skill in this codebase ever auto-submits a job application. Not now, not after the trigger conditions hit, not ever. The blast radius of a misfired submission to a real recruiter is too high.

> **Voice rules apply to every generated artifact.** [knowledge/writing_voice.md](knowledge/writing_voice.md) is the source of truth. No exceptions for "the agent did it."

> **New dependencies require explicit user approval.** The codebase defaults to stdlib-only. Adding Playwright, Selenium, or any other dep requires the user to say yes in writing.

> **Real applicant PII stays out of git.** Anything in `knowledge/applicant.json` with demographic data, DOB, or full home address is gitignored. The schema lives in the repo. The data does not.

---

## How to use this file

1. **Today:** read it, push back on anything that's wrong, ignore the rest. Don't build any of it.
2. **When trigger conditions hit:** re-read this file before opening a design doc.
3. **When designing:** create a separate `DESIGN.md` for the actual structure (state machine diagrams, handler interfaces, schema fields). This roadmap stays high-level.
4. **When something here turns out wrong:** edit it. Roadmaps are cheap to revise. Design docs are not.

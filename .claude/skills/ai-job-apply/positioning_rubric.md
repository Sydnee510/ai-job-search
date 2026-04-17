# Positioning Rubric

How to tailor each resume bullet so it reads at the seniority + scope the JD is looking for, without lying. Driven by `user_profile.json.career` + the JD's detected company stage.

## The core reframes

For every resume bullet, check whether the framing matches the JD's seniority expectation. Rewrite to lead with the right signal.

### If the JD is IC-facing (AI Engineer, Senior AI Engineer, Staff Engineer, Researcher, Designer, PM at an IC level)

Lead with **output and craft**: what you built, how it worked, what it moved. Scope signals (cross-functional leverage) are supporting, not headline.

| Generic framing | IC-facing framing (prefer) |
|---|---|
| "Led build of X" | "Built and shipped X using {stack}, {outcome}" |
| "Led cross-functional team" | Cut or demote — "partnered with {roles} to ship" works as a clause, not as the lead |
| "Owned the strategy" | Cut — strategy-first framing reads as manager-track to an IC interviewer |

### If the JD is leadership-facing (Lead, Staff-with-scope, EM, Director, Head of)

Lead with **scope and judgment**: who you led, what outcome, what tradeoff calls you made. Technical craft is supporting.

| IC framing (avoid as the lead) | Leadership reframe (prefer) |
|---|---|
| "Built X using Y" | "Led design and build of X" / "Drove architecture for X, shipped by a team of N" |
| "Wrote Z" | "Owned Z end-to-end, partnering with {roles}" |
| "Fixed bug/improved metric" | "Identified and led resolution of {problem} with {team}, shipping {outcome}" |
| "Helped with…" | Cut. If it's not ownership-level, it doesn't belong on a leadership resume. |
| "Contributed to…" | "Led the workstream on…" (only if true) |
| "Learned X" | Cut. Never. |

### What to surface prominently (leadership roles)

Hiring managers for leadership roles scan for:
1. **Scope** — How many people / systems / customers are affected by your work?
2. **Ownership** — Did you own an outcome, or just produce an artifact?
3. **Cross-functional leverage** — Did you coordinate product, design, other eng teams, execs?
4. **Judgment calls** — Did you make non-trivial tradeoff decisions?
5. **Outcome metrics** — Not just "shipped X" but "which moved Y by Z%"

The resume should already be metric-heavy. Keep every metric. Don't soften.

## Stage-adaptive bullet variants

For any bullet where stage-fit matters, `master_resume.md` should carry THREE variants. The skill picks one based on the JD's detected company stage.

### Variant selection rules

- **Early-stage (seed / Series A)** — pick `early-stage variant`. Emphasize 0→1, speed, ambiguity, small-team execution, full ownership.
- **Growth-stage (Series B–D)** — pick `growth-stage variant` (default). Balances scale and ownership.
- **Enterprise / FAANG** — pick `enterprise variant`. Emphasize scale, multi-team coordination, systems thinking, sub-second latency language, multi-provider / multi-model, compliance-aware.

### Worked example (generic template — replace with your own in master_resume.md)

**Bullet topic:** shipping a production AI feature with measurable impact.

**Source bullet (verbose baseline):**
> "Architected and deployed [PRODUCT_NAME] integrating [PRIMARY_AI_PROVIDER] APIs, [RUNTIME/FRAMEWORK], and [SECONDARY_PROVIDER] within a cloud-native architecture, enabling [BEHAVIOR] and onboarding [N]+ customers since [LAUNCH_DATE]."

**Early-stage variant:**
> "Led 0→1 build of [PRODUCT_NAME]: architected an LLM-backed pipeline on [PRIMARY_AI_PROVIDER], shipped to GA in <[N] months, onboarded [N]+ customers from public launch. Operated with small-team ambiguity: set scope, made stack calls, unblocked engineers."

**Growth-stage variant (default):**
> "Architected and deployed [PRODUCT_NAME] integrating [PRIMARY_AI_PROVIDER] APIs, [RUNTIME], and [SECONDARY_PROVIDER] within cloud-native microservices, onboarding [N]+ customers since [LAUNCH_DATE]. Led architecture calls across product and platform teams."

**Enterprise variant:**
> "Led architecture of production [DOMAIN] system: LLM orchestration across multi-provider stack ([PRIMARY], [SECONDARY]), serving [N]+ enterprise customers with consistent quality and cost envelopes. Partnered with platform, product, and SRE teams on scaling and reliability."

## Summary line — mirror the JD

The resume summary is the single highest-leverage line. Rewrite per application.

**Template:**
> "[ROLE_CATEGORY] with [X]y building [domain phrase from JD]. Currently [specific at current_employer matching JD scope]. Proven record of [the one outcome most relevant to the JD]."

Where `[ROLE_CATEGORY]` is chosen from the user's career framing:

- IC-facing target → "AI Engineer" / "Senior AI Engineer" / "ML Engineer" / "AI Product Manager" / "AI Researcher"
- Leadership-facing target → "Engineering Leader" / "AI Engineering Manager" / "Technical Leader with N+ years…"
- Player-coach hybrid → "AI Engineering Leader and hands-on builder" / "Engineering Manager track"

### Rules

- Use `user_profile.career.years_experience` verbatim. Pick ONE number and be consistent.
- Do not use: "passionate", "excited", "cutting-edge", "seamlessly", "leverage" (as a verb), "synergy", "proven track record of delivering" (see `knowledge/writing_voice.md` for the full banned list).
- First word should be a noun ("AI Engineer", "Engineering Manager track"), not a verb.

## Ordering the work experience section

Default order is chronological. For AI-native / AI-forward JDs, **keep chronological** — your most recent role is usually the most relevant. For JDs where your most recent role maps less directly, consider:
- Reordering bullets *within* a job entry to surface the matching one first
- Expanding the "Technical Projects" section to pull relevant open-source AI work closer to the top

Never reorder companies out of chronological order. It reads as deceptive.

## Managerial scope — honest framing

The skill reads `user_profile.career.is_people_manager` and `user_profile.career.direct_reports`.

### If `is_people_manager == true`

Use direct manager framing where true:
- "Managed a team of N engineers"
- "Hired and grew a team from N to M"
- "Owned career development for N direct reports"
- "Ran quarterly performance reviews and career ladder calibrations"

### If `is_people_manager == false` but the JD wants leadership

Use honest IC-leadership framing:
- "Technical lead for [team/product]"
- "Led architecture and technical direction for N engineers"
- "Cross-functional lead across product, engineering, and QA"
- "Mentored N engineers on [domain]"

**Do NOT say** (unless `direct_reports > 0` and story_bank documents it):
- "Managed a team of N"
- "Hired and grew a team"
- "Owned career development"

If the JD's must-have is formal people management and `is_people_manager == false`, the skill flags the role as a stretch in the fit score — and either (a) re-positions with honest IC-leadership framing or (b) surfaces the mismatch for the user to decide.

## Career-stage framing (`user_profile.career.career_stage`)

| Stage | Resume voice |
|---|---|
| `early` | Emphasize pace of learning, breadth, shipping. Tolerate less metric density. Don't oversell "owned" if you were supporting. |
| `mid` | Lead with shipped features + their outcomes. Start introducing tradeoff/decision language. |
| `senior` | Every bullet has a metric AND an ownership signal. Cross-functional leverage is the differentiator. |
| `principal` | Scope and organizational impact dominate. Technical depth is assumed; the differentiator is system-level or team-level judgment. |

## Technical projects — how to weight them

Open-source AI work is a high-signal differentiator for AI-native roles. The skill reads `master_resume.md`'s Technical Projects section and:

- **For AI-native / AI-forward roles:** promote the Technical Projects section above Volunteer Community Involvement. Include every project that touches AI.
- **For less-AI-focused roles:** keep one project (whichever is most on-point) and compress the others.

## When in doubt

Lean technical. The differentiation for most candidates applying to AI-specific roles is "builds production AI systems AND leads/ships well" — not "career generalist who happens to work at an AI company". Position accordingly.

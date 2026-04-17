# Master Resume — [YOUR NAME]

> **Source of truth for the resume tailoring pipeline.** Keep this updated as your career progresses.
> When the skill tailors a resume, it selects from the stage-adaptive bullet variants below.
> The skill reads `knowledge/user_profile.json` for name/contact; the Work Experience + Projects + Skills below is this file's job.

## Contact

Contact info lives in `knowledge/user_profile.json` (`contact.*` fields). The renderer pulls `name`, `email`, `phone`, `linkedin`, `github`, and optional `website` from there. You don't need to duplicate them here.

## Professional summary (default — rewritten per application per `positioning_rubric.md`)

> [YOUR_CAREER_CATEGORY] with [X]+ years of experience [short description of what you build]. Currently [current role scope at current_employer]. Proven record of [the one outcome you want recruiters to anchor on].

**Example filled version (replace with your own):**

> AI Native Engineer with 5+ years of experience building cloud-native SaaS platforms and production-grade AI systems. Currently leading development of [YOUR LATEST AI PROJECT] using [PRIMARY PROVIDERS AND RUNTIMES] to power [BEHAVIOR]. Proven record of shipping AI-driven platforms and translating complex business workflows into scalable AI systems.

> **TODO:** Write 2–3 variants of this summary — one for AI-native roles, one for AI-forward roles, one for AI-curious / traditional-with-AI-flavor roles. The skill picks based on JD classification.

---

## Work experience

### [CURRENT_COMPANY] — [LOCATION or Remote]
**[YOUR_CURRENT_TITLE]** · [MM/YYYY] – present

> **TODO:** If your current title doesn't match the role-level JDs are asking for (e.g. "Team Lead" vs "Engineering Manager"), note the honest framing here. The `positioning_rubric.md` handles this — see `user_profile.career.is_people_manager` and `direct_reports`.

**Bullet 1 — [TOPIC: e.g. the launch / the product / the metric]**

- *Early-stage variant:*
  "[Lead with 0→1 framing. Emphasize speed, ambiguity, small-team ownership. Include the metric.]"
- *Growth-stage variant (default):*
  "[Lead with scale + stack specifics. Include the metric.]"
- *Enterprise variant:*
  "[Lead with multi-team coordination + systems scope. Include the metric.]"

**Bullet 2 — [TOPIC]**

- *Early-stage variant:*
  "[Bullet text, ≤2 lines, ends in a number]"
- *Growth-stage variant (default):*
  "[Bullet text]"
- *Enterprise variant:*
  "[Bullet text]"

**Bullet 3 — [TOPIC]**

- *Early-stage variant:* "[...]"
- *Growth-stage variant (default):* "[...]"
- *Enterprise variant:* "[...]"

**Bullet 4 — [TOPIC]**

- *Early-stage variant:* "[...]"
- *Growth-stage variant (default):* "[...]"
- *Enterprise variant:* "[...]"

> **Rule:** every bullet ends in a metric. If you can't quantify it, either dig for the number or cut the bullet.

---

### [PREVIOUS_COMPANY] — [LOCATION]
**[ROLE_TITLE]** · [MM/YYYY] – [MM/YYYY]

- "[Bullet text ending in a metric.]"
- "[Bullet text ending in a metric.]"
- "[Bullet text ending in a metric.]"
- "[Bullet text ending in a metric.]"

> **Positioning note:** if this role isn't on-point for AI-focused JDs, keep these bullets but compress them for AI-native/AI-forward tailored versions.

---

### [EARLIER_COMPANY] — [LOCATION]
**[ROLE_TITLE]** · [MM/YYYY] – [MM/YYYY]

- "[Bullet text.]"
- "[Bullet text.]"
- "[Bullet text.]"

---

### [EARLIER_COMPANY] — [LOCATION]
**[ROLE_TITLE]** · [MM/YYYY] – [MM/YYYY]

- "[Bullet text.]"
- "[Bullet text.]"

> Add / remove entries as needed. Keep chronological order.

---

## Technical projects

> **Positioning note:** For AI-native / AI-forward roles, this section moves ABOVE volunteer work. For AI-specific projects, emphasize AI + open-source + workshop/community.

### [PROJECT_1_NAME] — [ONE_LINE_TAGLINE] (open source)
- Repo: [LINK_TO_REPO]
- Elevator: [1-line description].
- Bullets:
  - "[Bullet describing the technical work, naming the stack, ending in a metric or outcome.]"
  - "[Bullet describing the differentiator.]"

### [PROJECT_2_NAME] — [TAGLINE] (open source)
- Repo: [LINK]
- Elevator: [1-line description].
- Bullets:
  - "[Bullet.]"
  - "[Bullet.]"

### [PROJECT_3_NAME] — [TAGLINE]
- Bullets:
  - "[Bullet.]"
  - "[Bullet.]"

> **TODO:** Aim for 3–5 projects. At least 2 should be AI-specific if you're targeting AI roles. Link the repo if it's public.

---

## Volunteer community involvement

### [ORG_NAME] — [ROLE] · [MM/YYYY] – [present OR MM/YYYY]
- "[Bullet ending in a number: attendance, engagement, retention, members.]"
- "[Bullet.]"

### [ORG_NAME] — [ROLE] · [MM/YYYY] – [MM/YYYY]
- "[Bullet.]"
- "[Bullet.]"

> **TODO:** Keep this section short for AI-native roles (compresses below Technical Projects). Expand for people-first / community-focused roles.

---

## Skills

- **AI Systems:** [primary LLM providers you use], [any domain-specific providers], LLM integration, AI agent workflows, context engineering, RAG, multi-model AI platforms, model evaluation
- **Real-time systems:** [frameworks/runtimes you use for streaming], event-driven systems
- **API design and integration:** API best practices, documentation, integration architecture
- **DevOps and tools:** Docker, CI/CD, [your CI platform], logging, monitoring, observability
- **Programming languages:** [comma-separated]
- **Frameworks:** [comma-separated]

> **TODO:** Only list tech you've actually used. The `jd_analysis_rubric.md` cross-references this against the JD — if you claim "LangChain" here and the JD asks about it, you'd better be able to walk through a project where you used it.

---

## Education

- **[INSTITUTION]:** [PROGRAM / DEGREE]
- **[INSTITUTION]:** [PROGRAM / DEGREE]
- **[CERT_BODY]:** [CERTIFICATION], [YEAR]

> **TODO:** Include degrees, certifications, and any AI-specific credentials (e.g. Cornell Agentic AI, MIT DSML, any formal LLM/ML coursework).

---

## Editing notes

- Keep the metric-heavy, active-voice style. Do not soften.
- When tailoring, pick exactly ONE bullet variant per bullet — don't include multiple.
- Always check `positioning_rubric.md` before rewriting a bullet.
- If you add a new achievement to your current role, add THREE variants (early / growth / enterprise), not one.
- Never reorder companies out of chronological order.
- Never claim a tech or scope you don't have real experience with. The `story_bank.md` is the truth-check.

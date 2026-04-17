# Target Companies — AI Role Search

> **This is a seed list framework, not a research snapshot.** Before applying to any of these, the skill should WebSearch for:
> 1. Current openings at that company matching `user_profile.targeting.target_job_titles`
> 2. Recent funding / news (stage may have shifted)
> 3. Compensation signals (levels.fyi, LinkedIn, recent offers posted)
>
> **Warmth column:** mark connections or any insider signal you have. Update as you go.
> **Priority column:** A/B/C — A = apply this week, B = apply in 2 weeks if A doesn't progress, C = long-shot or distant stage fit.

---

## Tier 1 — AI-native (highest alignment)

Companies whose core product IS the AI. Strongest alignment for candidates with production AI experience.

| Company | Stage | Why it fits | Warmth | Priority | Notes |
|---|---|---|---|---|---|
| Anthropic | Growth (public-track) | Foundation model lab, Claude API + applied products | — | A | Check: roles matching your target titles |
| OpenAI | Growth (public-track) | Foundation model lab, broadest API surface | — | A | — |
| Cohere | Growth | Enterprise-focused LLM provider | — | B | — |
| Perplexity | Growth | Consumer + API AI, strong product-engineering culture | — | B | — |
| Hugging Face | Growth | OSS model hub, enterprise AI platform | — | B | — |
| Scale AI | Growth | Data + evals + enterprise AI | — | B | — |
| Glean | Growth | Enterprise search + AI assistants | — | B | — |
| Writer | Growth | Enterprise generative AI | — | B | — |

> **TODO:** Replace / expand with the companies you actually want. Remove rows that aren't on-point for your target titles. Add any domain specialists (voice, agents, evals, infra) that match your particular profile.

---

## Tier 2 — AI-forward at growth/scale (strong fit)

AI is a major product bet but not the whole company. Good fit for candidates whose profile is "applied AI at a SaaS company."

| Company | Stage | Why it fits | Warmth | Priority | Notes |
|---|---|---|---|---|---|
| Notion | Growth | Notion AI team | — | B | — |
| Linear | Growth | AI features team | — | B | — |
| [COMPANY] | [STAGE] | [why it fits your target] | — | [A/B/C] | — |

> **TODO:** Add companies where AI is a major product line but not the whole company. Good Tier 2 indicators: they have a named "AI team" or "Applied AI" group; recent product launches emphasize AI; engineering blog shows AI infra investment.

---

## Tier 3 — Domain-specialist companies

Specialists in your specific AI sub-domain (voice, agents, evals, infra, etc.). If you had to pick 5 companies to apply to this week, they'd often come from here.

| Company | Stage | Why it fits | Warmth | Priority | Notes |
|---|---|---|---|---|---|
| [DOMAIN_SPECIALIST_1] | [STAGE] | [direct domain match] | — | [A/B/C] | — |
| [DOMAIN_SPECIALIST_2] | [STAGE] | [direct domain match] | — | [A/B/C] | — |

> **TODO:** Add the 5–10 companies where your specific technical work maps most directly. This is usually your highest-conversion tier.

---

## Tier 4 — Stealth / early-stage

Search these weekly for new postings:

- **YC recent batches** — filter for AI / agents / voice / domain-specific AI companies, check their jobs pages directly
- **a16z portfolio AI companies** — a16z.com/portfolio, filter AI
- **Sequoia AI portfolio**
- **Index Ventures AI portfolio**
- **Greylock AI portfolio**

> **How to use:** Don't scatter applications. Pick 2–3 stealth/early roles per week that you've researched enough to lead with a real hook in the cover letter.

---

## Tier 5 — Out-of-scope (for reference only)

Companies to probably skip unless a specific unusual fit appears:

- **FAANG** — valuable compensation, but level signals and interview loops often require more seniority than the JD says. Only if you find a role that explicitly accepts your transition pattern.
- **Pure ML research labs** — DeepMind, FAIR, etc. Not an applied-AI profile.
- **Non-technical enterprises "adding AI"** — high risk of the buzzword trap flagged in `jd_analysis_rubric.md`.

> Adjust this section to reflect what's actually out of scope for YOU. "Out of scope" is personal.

---

## Tracking discipline

- When you add a company to `output/tracker.csv` via `tracker.py add`, **update this file too** — change the priority or move the company between tiers based on what you learn.
- When you get a rejection, write a one-liner: *why* did it not click? Stage mismatch? Scope mismatch? Something in the JD you didn't catch? That feeds back into the JD analysis rubric.

## Research workflow (for each target)

Before tailoring an application:
1. WebSearch for "[company] engineering blog"
2. WebSearch for "[company] compensation" / "[company] levels.fyi"
3. WebSearch for "[company] series [latest]" to confirm stage
4. Check LinkedIn for anyone in your network at the company
5. Check the company's recent product launches — use them as the specific hook in paragraph 3 of the cover letter

If you can't find anything specific to hook onto in the cover letter, don't apply yet. A generic cover letter is worse than no cover letter.

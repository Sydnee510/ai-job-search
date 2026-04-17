# STAR Story Bank

> **This file is the ONLY source of truth for cover letter narratives and interview stories.** The skill is instructed not to invent stories not captured here. If a question has no matching story, the skill will flag it as a `GAP:` rather than fake one.
>
> **TODO (you):** Fill each slot below. Don't write a polished essay — write honest bullets. You'll sharpen them per application. Leave `GAP:` if you don't have a story for a slot (that's useful data — it tells you where to pre-think).

## The 10 slots (one per archetypal interview question)

Cover each of these. If a single story covers two archetypes well, you can reference it in both — but make sure you've got 8–10 distinct stories total.

---

### Story 1 — 0→1 AI system ship

**Archetype:** "Walk me through an AI system you've shipped end to end."
**Most likely role category to use:** AI-native, AI-forward, any role emphasizing launch ownership.

**S — Situation:** *(What was the context? What was the business or product problem?)*
> *TODO: describe the problem + stakes. One sentence.*

**T — Task:** *(What specifically needed to happen, and why was it hard?)*
> *TODO: what needed to be true at the end, and what made it non-trivial.*

**A — Action:** *(What specifically did YOU do? Decisions, tradeoffs, leadership moves.)*
> *TODO: name the decisions you made — tech stack choice, scope call, architecture move, who you unblocked.*

**R — Result:** *(Quantified outcome.)*
> *TODO: numbers. Customers, speed, error rate, adoption, whatever is real.*

**Self-check before using this story:**
- Were you the architect, the tech lead, or the manager on this? Be precise.
- How many engineers shipped with you? What was YOUR scope vs. theirs?
- Were you involved in the stack-selection call, or was it made above you?

---

### Story 2 — AI latency / cost tradeoff

**Archetype:** "What's your approach to managing latency/cost tradeoffs in agentic systems?"
**Most likely role category:** AI-native, any real-time / voice / inference role.

**S:** *TODO*
**T:** *TODO*
**A:** *TODO — what you specifically did: measured P50/P95 per stage? parallelized tool calls? cached prompts? moved routing to a smaller model? streamed partial responses?*
**R:** *TODO — the latency or cost improvement in numbers.*

**GAP check:** If you don't have specific measurements / optimizations you personally led here, mark this story `GAP` and find a different angle. The skill won't fabricate.

---

### Story 3 — LLM evaluation in production

**Archetype:** "How do you evaluate LLM output quality in production?"
**Most likely role category:** AI-native, AI-forward.

**TODO:**
- Did you own evals for a production AI system? If yes, describe: what golden set, what online sampling, what guardrails, what regression tracking against model updates.
- If evals were someone else's scope, say so honestly. Your story can be "I pushed for eval discipline and this is what I'd do in a new role", not a fake "I built it".

---

### Story 4 — Difficult conversation with an engineer (manager-track) OR with a peer (IC)

**Archetype:** "Tell me about a time you had a difficult conversation with [an engineer / a peer]."
**Most likely role category:** Any role with an interpersonal lens.

**TODO:** Pick a real moment. Common versions:
- An engineer was missing deadlines and you had to address it.
- An engineer's design choice was wrong and you had to override it without damaging trust.
- A peer engineer was resistant to a decision you'd made.
- An engineer you'd mentored was underperforming.

**Looking for:** directness + empathy + outcome. Not "I was nice and it worked out" — the real move you made.

---

### Story 5 — Cross-functional conflict or alignment

**Archetype:** "Tell me about a conflict with a peer or cross-functional partner."
**Most likely role category:** Any role — near-certain question for senior + manager-track.

**TODO:** Pick one real one and write the STAR. Common shapes:
- Product wanted X; engineering thought X was wrong bet. How did you navigate?
- Client/customer expectation vs. internal reality. How did you manage?
- Two teams disagreed on an interface contract. How did you resolve?

Include the disagreement, your specific move, and the outcome (even if the outcome was "we compromised and both sides were slightly annoyed" — that's more honest than "everyone loved it").

---

### Story 6 — Project that shipped late / didn't go to plan

**Archetype:** "Tell me about a project that didn't go well."
**Most likely role category:** Any role.

**TODO:** Pick a real one. Avoid the "I was working too hard" humblebrag. Look for: you made a call that didn't pan out, or you misjudged scope, or a production incident went wrong. What did you learn and what would you do differently?

If everything you can think of is a success story, that's a signal to pre-think before interviews. Mark this `GAP` for now if needed.

---

### Story 7 — Mentorship / growing someone

**Archetype:** "How do you grow a [junior / less-senior] engineer?" / "Tell me about someone you mentored."
**Most likely role category:** People-first roles (manager-track), senior IC roles with mentorship expectations.

**TODO:** Pick ONE specific person (anonymize if needed). Walk the arc — where they started, what you did, where they ended up. Don't summarize "I've mentored many people" — tell one real story.

---

### Story 8 — Build vs. buy / technical judgment call

**Archetype:** "Walk me through a technical tradeoff you made."
**Most likely role category:** Technical-depth roles, architecture-leaning roles.

**TODO:** Pick one. Walk through the options you considered, the tradeoffs, the call you made, and what you'd do differently now. AI-specific examples:
- Why one LLM provider over another (capability? cost? latency? data privacy?)
- Why RAG over fine-tuning for a use case
- Why build the orchestration layer vs. buy a platform

---

### Story 9 — Managing ambiguity / small-team 0→1

**Archetype:** "Tell me about a time you had to figure it out with little direction."
**Most likely role category:** Seed / Series A roles. Founding-team roles.

**TODO:** Pick one. Typical shapes:
- Early-stage product work where the spec didn't exist.
- Founding or side-project work where you set the direction.
- A role you took on that had no predecessor.

---

### Story 10 — Why this role / why now / why this company

**Archetype:** "Why are you making this move?" / "Why leave [current employer]?"
**Most likely role category:** Every role asks some version.

**TODO:** Write your honest working draft here. Lean on `user_profile.career.leaving_reason_short` but expand:

> *TODO: 3–4 sentences. What you're doing now, what's next for you, what this role or company specifically offers that aligns. Don't bash the current employer.*

**Per-company tailoring goes at the end** — swap in one sentence specific to this company (something from their JD, blog, or product that's real).

---

## Additional slots (add as you build up stories)

### 11 — Production incident you led response on
### 12 — A hiring decision you're proud of (manager-track)
### 13 — A decision you'd make differently with hindsight
### 14 — Your first 30/60/90 days at your current (or a recent) role
### 15 — Time you changed your mind after initially disagreeing

Add bullets below each as you fill them in.

---

## Honesty rules for this file

1. **If you don't have a story, write `GAP` — don't invent one.** Gaps are signals, not failures. The skill will flag them in interview briefs so you can pre-think.
2. **Numbers are non-negotiable.** If you don't remember a number, write `TODO: get number` and dig it up. A story without a metric is a story without a result.
3. **Name what YOU did, not "we".** Cover letters and interviews are about your specific ownership. If it was a team effort, say so — but make your piece visible.
4. **Keep drafts short.** Don't polish here. Polish happens per application. Here we just need the raw material.

---

## Working-together notes

If you're filling these out with a coach, mentor, or AI assistant, a 90-minute session works best:
- 5 min: pick the 3 most common archetypes you're underpowered on
- 45 min: draft those three stories (15 min each)
- 20 min: draft the "why now / why them" answer (Story 10)
- 20 min: do quick bullet-drafts for Stories 1, 4, 5, 8 so you have minimum viable coverage
- Ship. Stories 2, 3, 6, 7, 9 get drafted as applications roll in.

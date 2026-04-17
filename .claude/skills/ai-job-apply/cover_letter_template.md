# Cover Letter Template

> **Before drafting, re-read `knowledge/writing_voice.md`.** The no-em-dash rule applies to every character of the output letter, even if this template file contains em-dashes in its meta-instructions.

Word budget: **250–300 words total**. If the draft hits 310, cut.

## Structure (four paragraphs, in this exact order)

### 1) Hook — single paragraph, 2–3 sentences

**Formula (for AI-native / AI-forward roles — use verbatim structure, swap the bracketed content):**

> At [CURRENT_EMPLOYER], I [LED_OR_BUILT] [SPECIFIC_AI_SYSTEM]: [SPECIFIC_TECHNICAL_CHALLENGE] with [SPECIFIC_OUTCOME]. That's the kind of [PROBLEM_PATTERN_FROM_JD] your team is taking on at [COMPANY].

Fill the bracketed content from the user's `master_resume.md` + `story_bank.md`:

- `[CURRENT_EMPLOYER]` = `user.career.current_employer`
- `[LED_OR_BUILT]` = "led the team that shipped" (for manager-track) OR "built and shipped" (for IC)
- `[SPECIFIC_AI_SYSTEM]` = the user's most on-point AI system, described in one clause (from `master_resume.md`)
- `[SPECIFIC_TECHNICAL_CHALLENGE]` = the hardest part of building it, in JD-relevant language
- `[SPECIFIC_OUTCOME]` = the metric from `master_resume.md` that most directly proves competence for this JD
- `[PROBLEM_PATTERN_FROM_JD]` = use the JD's own language. Examples: "grounded retrieval at production scale", "multi-model orchestration for agentic workflows", "applied AI that ships to real customers, not demos"
- `[COMPANY]` = the company name

If the user has no AI systems in `master_resume.md` that map to the JD, fall back to the strongest non-AI shipped-system story and flag the gap to the user.

### 2) Story — single paragraph, 4–5 sentences

Pick **one** story from `knowledge/story_bank.md` that maps to the JD's #1 requirement.

**For AI-native or AI-forward roles, the lead story MUST come from an AI-anchored slot in the story bank** (typically Story 1 — 0→1 AI system ship — or any technical-projects story in `master_resume.md`). Never lead with a non-AI story for AI roles.

Compress the story using STAR, but write it as prose, not as labeled sections:

- **Situation** (half a sentence) — context and stakes
- **Task** (half a sentence) — what needed to happen and why it was hard
- **Action** (2 sentences) — what the user specifically led/built, what tradeoffs they made
- **Result** (1 sentence, quantified) — the outcome in numbers

### 3) Why this company specifically — single paragraph, 3–4 sentences

**Rule:** reference something from the JD or the company that a boilerplate letter couldn't. Not "your mission resonates with me" — something real.

Good examples:
- "Your engineering blog on how you architect evals caught my attention. It mirrors the approach I've been pushing at [CURRENT_EMPLOYER]."
- "The [specific product area] work in your recent launch overlaps directly with the pipelines I've been building."
- "You're shipping applied AI into an industry that usually lags on it. I've been doing the equivalent for [user's current domain]."

Bad examples (do not write):
- "I'm excited about [Company]'s mission"
- "I've always admired [Company]"
- Anything that could be pasted into any other company's letter

### 4) Close — single sentence

**Formula:**
> I'd welcome a conversation about the [specific part of the role from the JD] and where I could be most useful from day one.

NOT: "I look forward to hearing from you." NOT: "Thank you for your consideration."

## Banned (zero tolerance in generated output)

**Characters:**
- **Em-dashes (`—`, U+2014) anywhere in the letter.** Top AI tell in the current hiring market. Use period, colon, or comma. See `knowledge/writing_voice.md` for full guidance.

**Phrases:**

- "I'm excited to apply"
- "I believe my experience"
- "I'm a perfect fit"
- "passionate about"
- "cutting-edge"
- "seamlessly"
- "leverage" (as a verb)
- "synergy"
- "best-in-class"
- "in today's fast-paced world"
- "proven track record of delivering"
- "ecosystem" when you mean "product" or "platform"

(See `knowledge/writing_voice.md` for the full AI-tell list.)

## Voice rules

- First-person, active voice. "I led" not "I was responsible for leading".
- Numbers > adjectives. "30% faster onboarding" not "significantly faster".
- Specific > general. Specific tech and provider names beat "modern AI technology".
- Concrete verbs: led, shipped, architected, owned, drove, built, scaled.
- No em-dashes. None. Use periods or colons.

## Sign-off

**Do NOT write a signoff into the cover letter `.md` body.** The HTML template at `knowledge/templates/cover_letter.html` automatically renders a properly styled signoff at the bottom of the PDF (themed "Best,", bold name, contact line) using values from `knowledge/user_profile.json`. Including it in the body produces a duplicate signature in the rendered PDF.

For reference, the signoff that the template auto-renders looks like:

```
Best,
{contact.name from user_profile.json}
{email | phone | linkedin [| github] from user_profile.json}
```

The body `.md` saved to disk should end with the close paragraph (the one-sentence "I'd welcome a conversation..." line). Nothing after it.

## Fully worked example — for reference only

**Scenario (placeholder content):** Senior AI Engineer at a Series B applied-AI company. Their JD emphasizes multi-model orchestration, production evals, and shipping directly to enterprise customers. The applicant is a senior engineer at a growth-stage SaaS company who has shipped a production RAG platform.

---

At [CURRENT_EMPLOYER], I built and shipped [PRODUCT_NAME]: a multi-tenant RAG platform integrating [PRIMARY_PROVIDER] APIs, a vector store, and structured-output grounding, with consistent quality across hundreds of enterprise workspaces. That's the kind of production applied-AI orchestration your team is taking on at [COMPANY].

The hardest part was the quality budget. Every answer had to be grounded, auditable, and defensible without slowing the assistant to a crawl. I made the call to standardize on [SPECIFIC_FRAMEWORK] over more abstracted alternatives, designed the retrieval-and-scoring pattern across tenants, and drove cross-functional alignment on which evals we'd ship against. Since public launch, we've onboarded [N]+ enterprise customers, cut support tickets [X]%, and moved answer-quality scores [Y]% higher.

The [specific product area] work in your recent post about [specific topic from their blog] is exactly the layer I've been building. You're also pushing on production evals in a way most applied-AI teams wave off, which matches how I've been operating. The eval story is usually the one that breaks teams at your stage. I'd rather work somewhere that takes it seriously.

I'd welcome a conversation about the applied-AI orchestration scope and where I could be most useful from day one.

---

Word count: ~280. That's the target. The body ends with the close paragraph above. The HTML template renders the styled "Best, / name / contact" signoff at the bottom of the PDF automatically — do not add it to the `.md`.

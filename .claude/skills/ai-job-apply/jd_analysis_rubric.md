# JD Analysis Rubric

Extract these signals from every job description. Be opinionated. If a signal is ambiguous, make a judgment call and note the uncertainty.

## 1. Role scope and level

Look for explicit or implicit signals about:
- **Seniority** — "Senior" / "Staff" / "Principal" / "Lead" / IC-new-grad. Cross-check against `user.targeting.target_seniority`.
- **Team size** (for manager-track roles) — "manage a team of 6", "growing team of 10+", or silence (silence usually means small, 2–5)
- **Org level** (for manager-track roles) — first-line EM, EM of EMs, senior EM, director-with-EM-scope. Language cues: "manage engineers" (line) vs "manage managers" (EM2) vs "set strategy" (director)
- **IC-player-coach vs pure management** — "write code 30% of the time", "technical leader who codes", "no coding expected" — each means something different
- **Hiring responsibility** (for manager-track roles) — "grow the team from X to Y" is a major signal; "maintain current team" is a different role

**Positioning rule:** cross-check the role's seniority against `user.career.career_stage` + `user.career.years_experience`. If the JD requires noticeably more (e.g. 10+ years when the user has 5), flag as a stretch. If the JD is noticeably junior (e.g. mid-level when user is principal), flag as a potential level-down.

## 2. AI depth classification (CRITICAL for this skill)

Classify into exactly ONE:

| Label | Signal | Positioning implication |
|---|---|---|
| **AI-native** | Core product IS the AI. JD talks about models, evals, inference, RL, or research. | **Highest fit** for AI-focused candidates — lead with AI-anchored stories from `master_resume.md` + `story_bank.md` |
| **AI-forward** | AI is a major product bet, not the whole company. JD mentions "AI feature", "AI product surface", "applied AI team". | **Strong fit** for applied-AI profiles |
| **AI-curious** | Company wants to "add AI" — greenfield, often a single hire asked to stand up the function. Can mean exciting 0→1 OR can mean buzzword-chasing with no infra. | **Contextual fit** — great if there's real budget and data, poor if it's a lone-wolf role at a non-technical company |
| **Traditional + AI flavor** | JD mentions AI once or twice but the actual work is something else (web platform, data eng, etc.). | **Low fit** for AI-focused candidates — skip unless comp/title/other factors are extraordinary |

## 3. Tech stack signals

Scan the JD for tech stack mentions. Cross-reference with what the user has in `master_resume.md` (skills section + project stacks).

Categorize each mention as:

- **STRONG MATCH** — user has experience per resume + story bank, JD calls for it. Flag as a keyword to preserve in the tailored resume.
- **ADJACENT** — user has something close but not identical (e.g. experience with a sibling framework; work with one provider when the JD asks for another). Note it as a clause, don't claim it flat-out.
- **GAP** — JD wants something the user hasn't worked with. If it's a must-have, it drops the fit score. If it's a nice-to-have, note it as a pre-interview study item.

Rules:
- Only claim STRONG MATCH on tech that actually appears in the user's resume or story bank. No stretching.
- Prefer multi-word matches ("real-time AI", "LLM evaluation") over single words — they're more discriminating.
- Note which keywords are already in the master resume vs which need to be added to a tailored version (honestly — no keyword stuffing).

## 4. Leadership archetype (for manager-track JDs) OR craft archetype (for IC JDs)

Pick the archetype the JD leans into:

### For manager-track roles

- **People-first** — "grow engineers", "career development", "coaching", "1:1s", "psychological safety". JD light on technical specifics. Positioning: lean on mentorship / community / teaching stories.
- **Delivery-focused** — "ship fast", "own outcomes", "drive execution", "operational excellence". JD mentions OKRs or metrics. Positioning: lean on shipped-at-scale stories with hard numbers.
- **Technical-depth** — "stay hands-on", "code reviews", "architecture decisions", "technical leader". JD names specific tech. Positioning: lead with architecture + open-source technical work.
- **Hybrid** — mentions all three roughly evenly. Most common. Positioning: weight toward technical-depth for AI roles, people-first as backup.

### For IC roles

- **Craft-focused** — "clean code", "thoughtful design", "code reviews". Positioning: lead with quality + taste stories.
- **Velocity-focused** — "ship fast", "iterate", "get to prod". Positioning: lead with 0→1 or feature-ship stories.
- **Depth-focused** — "deep expertise", "research", "novel problems". Positioning: lead with hardest-problem stories.
- **Breadth-focused** — "full-stack", "wear many hats", "founding engineer". Positioning: lead with multi-domain shipping stories.

## 5. Stage inference

Infer company stage even if not stated:

| Signals | Inferred stage |
|---|---|
| "Seed", <10 employees, "founding", no named investors | Pre-seed / seed |
| Series A/B mentioned, 30–100 employees, "hyper-growth" | Early growth |
| "Series C+", 100–500 employees, "scale the team" | Late growth |
| Public, "Fortune X", named divisions, >1000 employees | Enterprise / public |
| FAANG-tier names | FAANG |

**Default if unclear:** growth-stage. That's statistically most common for AI roles in current hiring markets.

Stage drives which **bullet variant** to use in the resume (see `positioning_rubric.md`).

## 6. Must-have vs nice-to-have

- **Must-haves** = "required", "must have", "you have", or unconditional statements
- **Nice-to-haves** = "bonus", "plus", "preferred", "ideally"

If a must-have is a real gap for the user (checked against `master_resume.md` + `story_bank.md` + `user_profile.json`), flag it prominently in the analysis output. The skill's main orchestration will ask whether to proceed.

Common must-have patterns to watch for:
- "N+ years managing direct reports" — check `user_profile.career.is_people_manager` and `direct_reports`
- "N+ years in [specific domain]" — check years_experience + resume bullets
- "Shipped X at scale" — check story_bank for quantified examples

## 7. Keywords for resume matching

Extract verbatim phrases likely to hit ATS / recruiter keyword scans. Rules:
- Only include keywords that **honestly apply** to the user's actual work.
- Prefer multi-word phrases ("real-time AI", "LLM evaluation") over single words.
- Note which keywords are already in the master resume vs which need to be added to a tailored version.

## 8. Red flags (DO NOT skip this step)

Flag any of these. Three or more → fit score auto-drops below 6.

**General:**
- Vague scope ("you'll wear many hats", "we'll figure it out as we go")
- Unrealistic scope for one person ("own the entire AI platform, hiring, and production incidents")
- No compensation band or a suspiciously low one
- Excessive "must-haves" (>10 bullets is usually a wishlist, not a real role)
- Culture language that reads as red-flag ("work hard play hard", "we're a family", "no ego")

**AI-specific:**
- "AI/ML" listed in requirements but no team or infra mentioned (buzzword role)
- Expected to "build an ML platform from scratch solo" at a non-technical company
- Vague ownership ("partner with data science team") with no clear scope of own team/work
- Salary band suspiciously low for AI specialization
- "Prompt engineer" or "AI evangelist" in the title for what's actually a different role (title inflation downward)
- JD name-drops 10+ tools with no indication which are actually in use
- "Looking for someone who's built GPT from scratch" at a non-research company (unrealistic / underpays for that skill)

## Output format

When you finish the analysis, produce the structured markdown block defined in `SKILL.md` Step 2. Keep it tight — the user skims this, they don't read it.

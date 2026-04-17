# Interview Prep Rubric

Use this to generate the one-page brief in the skill's main pipeline. Questions are organized by category. For each question, the skill should:
1. Pick the question(s) most likely for *this specific role* (using JD analysis)
2. Map to a specific story from `knowledge/story_bank.md` — name the story explicitly
3. If no story fits, mark the entry `GAP:` so the user knows to pre-think before the interview

The category mix for a given interview depends on `user_profile.targeting.target_job_families` + the JD. See `SKILL.md` Step 2 for the selection formula.

## A. People leadership (only if `user.career.is_people_manager == true` OR role is a manager-track role)

1. **"Tell me about a time you had a difficult conversation with an engineer."**
   - Looking for: directness + empathy + outcome
   - Map to: a story from story_bank about underperformance, missed deadline, or interpersonal conflict
2. **"How do you run 1:1s?"**
   - Looking for: structure but not rigidity, career growth vs. status-update balance
   - Map to: real 1:1 practice from the user's current or recent role
3. **"How do you grow a junior engineer into a senior one?"**
   - Looking for: concrete examples, not platitudes
   - Map to: mentorship stories from story_bank
4. **"How do you give critical feedback?"**
   - Looking for: a real example, the person's response, the outcome
5. **"Tell me about a time you had to let someone go or PIP someone."**
   - Likely GAP unless the user has this story — if so, flag prominently for pre-think
6. **"How do you build trust on a new team?"**
   - Map to: onboarding stories or new-role first-90-days stories

## B. Delivery / execution

1. **"Tell me about a project that shipped late. What happened?"**
   - Looking for: ownership, learning, not blame-shifting
   - GAP to check: does the user have a story that ISN'T about a happy-path ship?
2. **"How do you prioritize when everything is urgent?"**
   - Map to: real triage or crunch stories from story_bank
3. **"Walk me through how you'd run a sprint for a 5-person team."** (manager-track only)
   - Looking for: practical cadence, not Agile theater
4. **"How do you handle a production incident?"**
   - Map to: any real incident from story_bank — if none, GAP
5. **"How do you balance speed vs. quality?"**
   - Map to: a real shipping story where the tradeoff was explicit
6. **"Tell me about an OKR / goal that didn't hit and what you did."**
   - Looking for: honesty + adjustment mechanism

## C. Technical depth — AI/ML specific (ALWAYS at least 2 for AI roles)

1. **"Walk me through an AI system you've shipped end to end."**
   - Best story: whichever AI system the user has shipped most recently per `master_resume.md`. Cover: the core stack (provider/runtime/framework), the architecture choice, the customer-facing outcome, the metrics moved.
   - Tech decisions to be ready to defend: why that provider, why that framework, how they handled [key technical challenge in their system], how they scoped [relevant design concern].

2. **"How do you evaluate LLM output quality in production?"**
   - Frame: offline evals (golden sets) + online evals (sampling + human rating) + guardrails (schema validation, refusal detection) + regression tracking on model updates
   - Pull from: user's real eval work if it's in story_bank — flag GAP if not

3. **"What's your approach to managing latency/cost tradeoffs in LLM systems?"**
   - Frame: measure first (P50/P95/P99 per step), attribute (model vs. network vs. tool calls), then optimize — smaller models for routing, caching prompts, parallel tool calls, streaming where possible
   - Pull from: real perf work if documented — flag GAP if no specific examples

4. **"How do you handle hallucinations at the product level?"**
   - Frame: constrain (RAG grounding, structured outputs, retrieval), detect (confidence scoring, fact-check passes), contain (graceful fallbacks, clear UX disclaimers), measure (hallucination rate in evals)
   - Pull from: user's RAG / grounding stories from story_bank

5. **"When would you fine-tune vs. prompt vs. RAG?"**
   - Frame: RAG for knowledge freshness / specificity / citations; prompting for behavior / format / tone; fine-tuning only when behavior doesn't stabilize via prompting AND real training data exists AND cost/latency justifies it. Default to RAG+prompting; treat fine-tuning as a last resort for most applied AI teams.
   - Pull from: user's own build-vs-buy or provider-choice story

6. **"Walk me through a tradeoff between build and buy for AI infra."**
   - Frame: buy for undifferentiated infra (model inference, managed retrieval, managed deployment); build for the parts that are your moat (orchestration, product-specific evals, UX-specific guardrails)
   - Pull from: story from story_bank where user made a buy/build call

7. **"What's your take on open-source vs. closed models?"**
   - Frame: closed (Claude, GPT) for fastest capability and hosted ops; open-source (Llama, Mistral) for cost, latency, data-privacy-sensitive verticals. Not a religious choice — depends on the use case. Be honest about what the user has actually deployed.

## D. Team / hiring in AI-specific contexts (manager-track)

1. **"How do you manage engineers when the tech stack changes every 3 months?"**
   - Frame: invest in durable fundamentals (evals, systems thinking, product judgment) over specific frameworks. Create a learning budget. Encourage small pilots over big rewrites.
2. **"How do you hire for AI roles when the field is so new?"**
   - Frame: look for systems thinking + product sense + willingness to learn; avoid over-indexing on a specific stack. Ask for real projects, not Kaggle scores.
3. **"How do you balance research-y exploration with shipping?"**
   - Frame: time-boxed exploration sprints with clear "ship or kill" criteria; separate research from production infra; force early integration tests before scaling investment
4. **"How do you handle the gap between ML researchers and application engineers?"**
   - Frame: shared language (eval dashboards both teams trust), shared responsibility (researchers on-call for model regressions), shared artifacts (versioned models, reproducible eval sets)
   - Flag as GAP if the user hasn't worked directly with researchers

## E. Strategic / judgment (always 1)

1. **"When does a feature need an LLM vs. traditional ML vs. rules?"**
   - Frame: rules for deterministic + low-variance; traditional ML for structured prediction with real training data; LLM for open-ended language, long-tail, zero-shot, or when speed-to-market beats accuracy. Cost and latency shape the choice.
2. **"What would your first 30/60/90 days look like here?"**
   - Frame (customize per JD): 30 = listen, 1:1 with every team member and key stakeholders, ship one small thing to earn trust; 60 = own a roadmap item, start making calls on scope, begin writing decisions; 90 = visible shift in team outcomes — faster cycles, better evals, or clearer prioritization.
3. **"What's a technical bet you'd make for our team if hired?"**
   - Requires JD-specific prep. Always pre-research before interview. GAP if no specific take.

## F. Behavioral / culture

1. **"Why this role / why now?"**
   - Lean on `user.career.leaving_reason_short` as the kernel, then tailor: honest answer about what's next, what the user's current role doesn't offer, what this role specifically does.
2. **"Why are you leaving [current employer]?"**
   - Adapt `user.career.leaving_reason_short`. Don't bash the current employer. Frame as "I shipped X; the next chapter I want is Y; the timeline there isn't what I want, so I'm looking."
3. **"Tell me about a conflict with a peer / cross-functional partner."**
   - Map to: story from story_bank (Story 5 slot)
4. **"What's a mistake you made as a leader?"** (manager-track) / **"What's a mistake you made?"** (IC)
   - Must have a real answer. Common traps: micromanaging under pressure; waiting too long to give feedback; taking on too much IC work; not escalating fast enough.

## G. Craft / depth (for IC roles specifically)

1. **"Walk me through your cleanest piece of code."**
   - Map to: a project from user's Technical Projects section that demonstrates taste
2. **"What's something you had to rebuild from scratch, and why?"**
   - Map to: real refactor or rebuild story
3. **"How do you decide when a design is done?"**
   - Frame: reviewable by someone who wasn't in the room; handles the 3 most obvious failure modes; has one clear owner for the rollout

## Three smart questions (tailored per JD)

Never ask generic "what's the culture like". Always tailor to the JD. Templates:

- **If JD emphasizes greenfield AI:** "What's already built vs. what you're expecting this hire to start from zero? And what's the product bet that justifies the investment?"
- **If JD emphasizes scale:** "What's the current scaling bottleneck — engineering throughput, model quality, infra cost, or something else?"
- **If JD mentions multi-model / multi-provider:** "How do you decide when to bring a new model provider into the stack — is there an eval framework or is it more judgment-call?"
- **If JD is vague about scope:** "What are the 2–3 outcomes I'd be evaluated on at 6 months?"
- **If JD emphasizes team growth** (manager-track): "What's the hiring plan for this team in the next 12 months, and what's this role's part in shaping it?"
- **If JD is AI-native / research-adjacent:** "How does the team balance research-style exploration with shipping to production? Is there a formal split or does it live in the same roadmap?"
- **If JD is at a non-AI-native company:** "What's the internal story on AI — is the org aligned on its role in the product, or is this hire partly responsible for making that case?"
- **If JD is an IC role:** "What does a great first project look like for someone in this role?"

Always have a closer: "Is there any concern about my fit that I can address right now before we wrap?" — this is high-signal and most candidates don't ask it.

## Gap-flagging discipline

When the skill generates an interview brief, it MUST be honest about gaps. If the user doesn't have:
- A clean "fired / PIP'd someone" story
- A production incident with direct-response ownership
- Direct reports with formal career development responsibility (check `user_profile.career.is_people_manager`)
- Experience with ML researchers specifically
- Any other likely-question archetype

…then flag each as `GAP:` in the brief so the user can pre-think before the interview. Do not paper over with a weak analog.

## Output format

The brief should be a single markdown file, ~1 page when printed. See `SKILL.md` for the required structure.

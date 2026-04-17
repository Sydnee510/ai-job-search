# User Profile Schema

> **Single source of truth for user data across all `ai-job-*` skills.** Every skill auto-injects `knowledge/user_profile.json` at load time. Edit it once and the whole system uses your values.

This file documents every field. `knowledge/user_profile.json` is the live template you edit. If you add new fields over time, document them here so future-you (and fork users) understand what they do.

## This works for any role — not just AI

The project name and default examples lean AI because that's where the original author targeted. The system itself is **role-agnostic**. The ATS polling, resume tailoring, cover-letter drafting, interview-prep questions, and pipeline tracking all work for any knowledge-work role.

Examples of roles forkers have used it (or could use it) for:

| Role family | Starter `target_job_titles` |
|---|---|
| AI / ML Engineer | `["AI Engineer", "Senior AI Engineer", "ML Engineer"]` |
| AI Product Manager | `["AI Product Manager", "Senior Product Manager, AI"]` |
| Engineering Manager | `["Engineering Manager", "Senior Engineering Manager", "Director of Engineering"]` |
| Software Engineer | `["Software Engineer", "Senior Software Engineer", "Backend Engineer"]` |
| UX Designer | `["UX Designer", "Senior Product Designer", "Staff Product Designer"]` |
| Technical Program Manager | `["Technical Program Manager", "Senior TPM"]` |
| Cybersecurity | `["Security Engineer", "Cybersecurity Analyst", "AppSec Engineer"]` |
| Data Scientist | `["Data Scientist", "Senior Data Scientist", "Applied Scientist"]` |
| Data Engineer | `["Data Engineer", "Analytics Engineer"]` |
| Developer Advocate | `["Developer Advocate", "Developer Relations Engineer"]` |
| Researcher | `["Research Scientist", "Applied Researcher"]` |

`knowledge/user_profile.json` ships with these lists pre-populated in its `_role_examples` block — copy one into `targeting.target_job_titles` to start.

**If you target non-AI roles, also edit `.claude/skills/ai-job-discover/discover.py` → `AI_BOOST_PATTERNS`** to boost title keywords relevant to your field (e.g. swap `\bai\b` for `\bsecurity\b` or `\bdesigner\b`). The title-inclusion filter `EM_PATTERNS`/`EXCLUDE_PATTERNS` also leans toward engineering-management titles today — adjust if needed. See the inline comments in `discover.py`.

---

## `contact`

Who you are, how to reach you, and how to sign resumes + cover letters.

| Field | Type | Required | Description |
|---|---|---|---|
| `contact.name` | string | yes | Your full legal or preferred name. Renders as the name block at the top of resumes and cover letter PDFs. |
| `contact.email` | string | yes | Email address recruiters will see on your resume. |
| `contact.phone` | string | yes | Phone in any format. Rendered verbatim on the contact line. |
| `contact.linkedin` | string | yes | LinkedIn URL or handle. Don't include `https://` — the templates add it. |
| `contact.github` | string | no | GitHub URL or handle. Used on resume contact line AND as the HTTP User-Agent contact when discover.py polls ATSes (so recruiters/ATS ops can find you if they trace a request). |
| `contact.website` | string or null | no | Personal site URL. Only rendered if set. |
| `contact.location_city` | string | yes | Your city + state. Used to auto-detect when a JD is close to you and for cover letter context. |

---

## `targeting`

What roles you want to apply for. `ai-job-discover` uses these to filter ATS results; `ai-job-apply` uses them to frame the resume summary.

| Field | Type | Description |
|---|---|---|
| `targeting.target_job_titles` | array of strings | The EXACT titles you want. Example: `["AI Engineer", "Senior AI Engineer", "Engineering Manager, AI"]`. Discover matches these against ATS titles (case-insensitive, word-boundary). Be specific: "AI Engineer" matches a lot of noise; "Senior AI Engineer" is cleaner. |
| `targeting.target_seniority` | array of strings | Seniority levels you'll accept. Common values: `["junior", "mid", "senior", "staff", "principal", "lead"]`. Used for title regex expansion. |
| `targeting.target_job_families` | array of strings | Higher-level job families for the discovery rubric (e.g. "AI Engineer", "AI PM", "AI Researcher", "AI Designer"). Controls which question categories the interview-prep skill weights. |
| `targeting.avoid_title_patterns` | array of strings | Substrings that auto-exclude a posting. Default excludes interns, coordinators, etc. Add patterns like `"Sales"` if recruiters keep surfacing wrong-function roles with AI in the title. |

---

## `career`

Current role context + career stage. Drives resume positioning (IC vs leadership, bullet variant selection) and cover letter framing ("I'm leaving X because Y").

| Field | Type | Description |
|---|---|---|
| `career.career_stage` | enum | One of `early` \| `mid` \| `senior` \| `principal`. Drives which bullet variant the skill picks from `master_resume.md` when tailoring. Independent of the COMPANY stage the JD describes (that's detected from JD text). |
| `career.years_experience` | integer | Total years of professional experience. Used verbatim in resume summary ("X+ years building..."). Pick one number and keep it consistent with your LinkedIn and resume PDF. |
| `career.current_role` | string | Your current job title. Used in cover letter opener framing. |
| `career.current_employer` | string | Your current company name. Used for "at [employer], I led..." openers in cover letters. Use `[UNEMPLOYED]` or omit if you're between roles. |
| `career.current_employer_stage` | enum | One of `seed` \| `early` \| `growth` \| `enterprise` \| `faang`. Helps the positioning rubric frame your experience for JDs at different-stage companies. |
| `career.is_people_manager` | boolean | **Critical.** True if you have direct reports with performance review responsibility. False if you're a team lead, tech lead, or IC. Drives honesty rules in the positioning rubric (no claiming "managed a team of N" if false). |
| `career.direct_reports` | integer | Number of direct reports (0 if `is_people_manager` is false). Used in resume bullets when applying to EM/Director roles. |
| `career.leaving_reason_short` | string | One-sentence honest answer to "why are you leaving?" Used as a starting draft in the story bank and interview brief. Refine per company. |

---

## `locations`

Ranked list of your preferred work locations. Every role ATS-polled gets its location checked against this list; matches add to the role's ranking score. Replaces the older `preferences.json` (merged in).

Each entry:

| Field | Type | Description |
|---|---|---|
| `name` | string | Canonical display name. Rendered in discover reports. |
| `weight` | integer | Added to a role's score when the location matches. Higher = stronger preference. Typical range 1–10. |
| `aliases` | array of strings | Alternate spellings the matcher accepts. Matched at word boundaries, case-insensitive (so `"GA"` doesn't match `"Bangalore"`). |
| `min_base_usd` | integer (optional) | If set, any matching role is flagged `needs_comp_verification: true` with a "verify base >= $X" tag. ATS APIs rarely include salary, so this is a reminder flag, not a hard filter. |

Order doesn't matter for matching — each role checks all locations and takes the first match. But put your top priority first for readability.

---

## Top-level `hybrid_ok`

Boolean. If `true`, hybrid roles at preferred cities count as matches. If `false`, only fully-remote and on-site-in-preferred-city count. Default: `true`.

---

## `compensation`

| Field | Type | Description |
|---|---|---|
| `compensation.min_base_usd_default` | integer | Baseline minimum base you'll consider anywhere. Informational only — NOT a hard filter (most ATSes don't expose salary). The skills use it to flag "likely under your floor" roles in analysis. |
| `compensation.comp_gates` | object | Per-city overrides of the default. Key is the lowercased city name. Duplicates `locations[].min_base_usd` for convenience when scanning. Keep them in sync. |

---

## `agent_runtime`

Runtime knobs for the Python scripts. You usually don't need to touch these.

| Field | Type | Description |
|---|---|---|
| `agent_runtime.user_agent_contact` | string or null | What goes in the HTTP `User-Agent` header when `discover.py` polls ATSes. Defaults to your GitHub URL. Leave `null` or empty if you want a generic UA. |
| `agent_runtime.chrome_binary` | string or null | Override Chrome's path for PDF rendering. Normally autodetected. Use this only if Chrome isn't in a standard location. |

---

## How skills read this file

Every `SKILL.md` in `.claude/skills/ai-job-*/` injects this file's contents at load time via:

```
## User profile (auto-injected at skill load)
```!
cat knowledge/user_profile.json
```
```

The skill treats the injected JSON as the source of truth for `user.name`, `user.email`, `user.targeting.*`, etc. When tailoring outputs, it pulls from this object rather than hardcoding values.

The Python scripts (`render_pdf.py`, `discover.py`, `tracker.py`) also read this file directly where needed (e.g. `render_pdf.py` reads `contact.name` + the assembled contact line for cover letter PDFs).

---

## Adding a new field

1. Add it to `user_profile.json` with a sensible default.
2. Document it in this file.
3. Update whichever skill consumes it.
4. Keep backwards-compatible defaults so old user profiles don't break.

#!/usr/bin/env python3
"""
render_pdf.py — render a tailored resume or cover letter to PDF.

Uses Chrome headless for the HTML → PDF step (no external Python deps).
Templates live at <project_root>/knowledge/templates/{resume,cover_letter}.html.

By default writes only the .pdf. Pass --keep-html to also persist the
intermediate .html beside the PDF (useful when debugging template / font
/ spacing issues). The .html can always be regenerated from the .md.

Usage
-----
Output paths follow knowledge/output_conventions.md:
  output/{YYYY-MM-DD}/{company_slug}/{company_slug}_{role_slug}_{kind}.{ext}

    # Resume
    python3 render_pdf.py resume \
        --input  output/2026-04-16/anthropic/anthropic_em-applied-ai_resume.md \
        --pdf    output/2026-04-16/anthropic/anthropic_em-applied-ai_resume.pdf

    # Cover letter
    python3 render_pdf.py cover-letter \
        --body       output/2026-04-16/anthropic/anthropic_em-applied-ai_cover.md \
        --company    "Anthropic" \
        --salutation "Dear Anthropic Team," \
        --date       "April 16, 2026" \
        --pdf        output/2026-04-16/anthropic/anthropic_em-applied-ai_cover.pdf

Project root is auto-resolved from this script's location.
Override with env var AI_JOB_PROJECT_ROOT.

Cover-letter --name and --contact default to the values in
knowledge/user_profile.json (contact.name + assembled email|phone|linkedin line).
Pass them explicitly to override.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import datetime
from pathlib import Path

# ---------- Paths ----------

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
PROJECT_ROOT = Path(os.environ.get("AI_JOB_PROJECT_ROOT", DEFAULT_PROJECT_ROOT))
TEMPLATES_DIR = PROJECT_ROOT / "knowledge" / "templates"
USER_PROFILE = PROJECT_ROOT / "knowledge" / "user_profile.json"


def _load_user_profile() -> dict:
    """Best-effort load of knowledge/user_profile.json.
    Returns {} if missing or invalid so the CLI can fall back to explicit flags."""
    if not USER_PROFILE.exists():
        return {}
    try:
        with USER_PROFILE.open() as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _default_name() -> str:
    contact = _load_user_profile().get("contact") or {}
    return contact.get("name") or ""


def _default_contact_line() -> str:
    """Assemble the contact line shown on resume + cover letter PDFs.
    Format: 'email | phone | linkedin[ | github][ | website]' — missing fields are skipped."""
    contact = _load_user_profile().get("contact") or {}
    parts = [
        contact.get("email"),
        contact.get("phone"),
        contact.get("linkedin"),
        contact.get("github"),
        contact.get("website"),
    ]
    return " | ".join(p for p in parts if p)

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
]


def find_chrome() -> str:
    for path in CHROME_CANDIDATES:
        if Path(path).exists():
            return path
    for name in ("google-chrome", "chromium", "chromium-browser"):
        which = shutil.which(name)
        if which:
            return which
    sys.exit("Chrome / Chromium not found. Install Chrome or set CHROME env var.")


# ---------- Minimal markdown → HTML helpers ----------

BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITAL_RE = re.compile(r"(?<!\*)\*([^\*\n]+?)\*(?!\*)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def inline_md(text: str) -> str:
    """Convert inline markdown (bold, italic, links) in a single line to HTML.
    Escapes HTML first, then re-inserts the tags."""
    escaped = html.escape(text, quote=False)
    escaped = LINK_RE.sub(r'<a href="\2">\1</a>', escaped)
    escaped = BOLD_RE.sub(r"<strong>\1</strong>", escaped)
    escaped = ITAL_RE.sub(r"<em>\1</em>", escaped)
    return escaped


def paragraphs(text: str) -> list[str]:
    """Split a chunk of text into paragraphs by blank-line boundaries."""
    blocks = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return blocks


# ---------- Resume parser ----------

class ResumeDoc:
    """Parses the skill's tailored resume markdown into structured sections."""

    def __init__(self, md: str):
        self.name = ""
        self.contact = ""
        self.sections: dict[str, str] = {}  # section title lowercased → raw section body
        self._parse(md)

    def _parse(self, md: str) -> None:
        lines = md.splitlines()
        # First line(s): name + contact
        i = 0
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i < len(lines) and lines[i].startswith("# "):
            self.name = lines[i][2:].strip()
            i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i < len(lines) and not lines[i].startswith("#"):
            self.contact = lines[i].strip()
            i += 1
        # Remaining: sections keyed by ## headers
        current_title = None
        current_buf: list[str] = []
        for line in lines[i:]:
            if line.startswith("## "):
                if current_title is not None:
                    self.sections[current_title.lower()] = "\n".join(current_buf).strip()
                current_title = line[3:].strip()
                current_buf = []
            else:
                current_buf.append(line)
        if current_title is not None:
            self.sections[current_title.lower()] = "\n".join(current_buf).strip()

    def section(self, title: str) -> str:
        return self.sections.get(title.lower(), "")


# ---------- Resume section renderers ----------

ENTRY_HEADER_RE = re.compile(r"^(.+?)\s+[—–-]\s+(.+)$")


def render_summary(text: str) -> str:
    # Just a paragraph; collapse whitespace
    return inline_md(" ".join(text.split()))


def _parse_entries(section_md: str) -> list[tuple[str, list[str]]]:
    """Split a section into entries by ### markers.
    Returns list of (header_line, body_lines)."""
    entries: list[tuple[str, list[str]]] = []
    current_header: str | None = None
    current_body: list[str] = []
    for line in section_md.splitlines():
        if line.startswith("### "):
            if current_header is not None:
                entries.append((current_header, current_body))
            current_header = line[4:].strip()
            current_body = []
        elif current_header is not None:
            current_body.append(line)
    if current_header is not None:
        entries.append((current_header, current_body))
    return entries


def _render_bullets(body_lines: list[str]) -> str:
    items = [l.strip()[2:].strip() for l in body_lines if l.strip().startswith("- ")]
    if not items:
        return ""
    lis = "\n".join(f"    <li>{inline_md(it)}</li>" for it in items)
    return f'  <ul class="bullets">\n{lis}\n  </ul>'


def render_work_experience(section_md: str) -> str:
    """Each entry: `### Company — Location` followed by `**Role** · dates` then bullets."""
    out: list[str] = []
    for header, body in _parse_entries(section_md):
        m = ENTRY_HEADER_RE.match(header)
        if m:
            company, location = m.group(1).strip(), m.group(2).strip()
        else:
            company, location = header, ""
        # First non-empty body line is the role line
        body_stripped = [l for l in body if l.strip()]
        role_line = body_stripped[0] if body_stripped else ""
        # role_line is expected like: **Role Title** · dates
        role_html = ""
        dates_html = ""
        if "·" in role_line:
            role_part, date_part = role_line.split("·", 1)
            role_html = inline_md(role_part.strip())
            dates_html = inline_md(date_part.strip())
        else:
            role_html = inline_md(role_line.strip())
        bullets_html = _render_bullets(body_stripped[1:])
        entry = (
            '<div class="entry">\n'
            '  <div class="entry-header">\n'
            f'    <span class="entry-company">{inline_md(company)}</span>\n'
            f'    <span class="entry-location">{inline_md(location)}</span>\n'
            '  </div>\n'
            '  <div class="entry-role-line">\n'
            f'    <span class="entry-role">{role_html}</span>\n'
            f'    <span class="entry-dates">{dates_html}</span>\n'
            '  </div>\n'
            f'{bullets_html}\n'
            '</div>'
        )
        out.append(entry)
    return "\n".join(out)


def render_projects(section_md: str) -> str:
    """Each entry: `### Project Name` optional subtitle, then bullets."""
    out: list[str] = []
    for header, body in _parse_entries(section_md):
        body_stripped = [l for l in body if l.strip()]
        subtitle = ""
        bullet_start = 0
        if body_stripped and not body_stripped[0].strip().startswith("- "):
            subtitle = body_stripped[0]
            bullet_start = 1
        bullets_html = _render_bullets(body_stripped[bullet_start:])
        subtitle_html = (
            f'  <div class="project-subtitle">{inline_md(subtitle)}</div>\n'
            if subtitle else ""
        )
        out.append(
            '<div class="project entry">\n'
            f'  <div class="project-title">{inline_md(header)}</div>\n'
            f'{subtitle_html}'
            f'{bullets_html}\n'
            '</div>'
        )
    return "\n".join(out)


def render_volunteer(section_md: str) -> str:
    """Each entry: `### Org — Role · dates` then bullets."""
    out: list[str] = []
    for header, body in _parse_entries(section_md):
        # Split on final " · " if present for date on the right
        if "·" in header:
            main, dates = header.rsplit("·", 1)
            main_html = inline_md(main.strip())
            dates_html = inline_md(dates.strip())
        else:
            main_html = inline_md(header)
            dates_html = ""
        body_stripped = [l for l in body if l.strip()]
        bullets_html = _render_bullets(body_stripped)
        out.append(
            '<div class="entry">\n'
            '  <div class="entry-role-line">\n'
            f'    <span class="entry-role"><strong>{main_html}</strong></span>\n'
            f'    <span class="entry-dates">{dates_html}</span>\n'
            '  </div>\n'
            f'{bullets_html}\n'
            '</div>'
        )
    return "\n".join(out)


def render_bullet_list(section_md: str, css_class: str) -> str:
    items = [
        l.strip()[2:].strip()
        for l in section_md.splitlines()
        if l.strip().startswith("- ")
    ]
    if not items:
        return ""
    lis = "\n".join(f"  <li>{inline_md(it)}</li>" for it in items)
    return f'<ul class="{css_class}">\n{lis}\n</ul>'


# ---------- Top-level render functions ----------

def render_resume(md_path: Path, out_pdf: Path, keep_html: bool = False) -> None:
    md = md_path.read_text()
    doc = ResumeDoc(md)
    template = (TEMPLATES_DIR / "resume.html").read_text()

    replacements = {
        "{{NAME}}": html.escape(doc.name, quote=False),
        "{{CONTACT_LINE}}": inline_md(doc.contact),
        "{{SUMMARY}}": render_summary(doc.section("Professional Summary")),
        "{{WORK_EXPERIENCE_BLOCK}}": render_work_experience(doc.section("Work Experience")),
        "{{PROJECTS_BLOCK}}": render_projects(doc.section("Technical Projects")),
        "{{VOLUNTEER_BLOCK}}": render_volunteer(doc.section("Volunteer Community Involvement")),
        "{{SKILLS_BLOCK}}": render_bullet_list(doc.section("Skills"), "skills-list"),
        "{{EDUCATION_BLOCK}}": render_bullet_list(doc.section("Education"), "education-list"),
    }
    html_out = template
    for k, v in replacements.items():
        html_out = html_out.replace(k, v)
    _html_to_pdf(html_out, out_pdf, keep_html=keep_html)


def render_cover_letter(
    body_path: Path,
    out_pdf: Path,
    company: str,
    salutation: str,
    date_str: str,
    name: str,
    contact: str,
    keep_html: bool = False,
) -> None:
    body_md = body_path.read_text().strip()
    paras = paragraphs(body_md)
    paragraphs_html = "\n    ".join(f"<p>{inline_md(p)}</p>" for p in paras)

    template = (TEMPLATES_DIR / "cover_letter.html").read_text()
    replacements = {
        "{{NAME}}": html.escape(name, quote=False),
        "{{CONTACT_LINE}}": inline_md(contact),
        "{{COMPANY}}": html.escape(company, quote=False),
        "{{DATE}}": html.escape(date_str, quote=False),
        "{{SALUTATION}}": html.escape(salutation, quote=False),
        "{{BODY_PARAGRAPHS}}": paragraphs_html,
    }
    html_out = template
    for k, v in replacements.items():
        html_out = html_out.replace(k, v)
    _html_to_pdf(html_out, out_pdf, keep_html=keep_html)


# ---------- HTML → PDF via Chrome headless ----------

def _html_to_pdf(html_str: str, out_pdf: Path, keep_html: bool = False) -> None:
    chrome = os.environ.get("CHROME") or find_chrome()
    out_pdf = out_pdf.resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_html = Path(tmpdir) / "render.html"
        tmp_html.write_text(html_str)
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=2000",
            f"--print-to-pdf={out_pdf}",
            tmp_html.as_uri(),
        ]
        try:
            subprocess.run(cmd, check=True, cwd=tmpdir, capture_output=True)
        except subprocess.CalledProcessError:
            cmd[1] = "--headless"
            try:
                subprocess.run(cmd, check=True, cwd=tmpdir, capture_output=True)
            except subprocess.CalledProcessError as e2:
                sys.exit(
                    "Chrome headless PDF export failed.\n"
                    f"Command: {' '.join(cmd)}\n"
                    f"Stderr: {e2.stderr.decode(errors='replace') if e2.stderr else ''}"
                )

    print(f"PDF:  {out_pdf}")
    if keep_html:
        out_html = out_pdf.with_suffix(".html")
        out_html.write_text(html_str)
        print(f"HTML: {out_html}  (kept for debugging)")


# ---------- CLI ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="render ai-job-apply output to PDF")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("resume", help="render a tailored resume markdown to PDF")
    r.add_argument("--input", required=True, type=Path, help="path to tailored resume .md")
    r.add_argument("--pdf", required=True, type=Path, help="output pdf path")
    r.add_argument("--keep-html", action="store_true", help="also save the intermediate .html beside the PDF (debug)")

    c = sub.add_parser("cover-letter", help="render a cover-letter body markdown to PDF")
    c.add_argument("--body", required=True, type=Path, help="path to cover letter body .md (just the paragraphs)")
    c.add_argument("--company", required=True)
    c.add_argument("--salutation", default="Dear Hiring Team,")
    c.add_argument(
        "--date",
        default=datetime.date.today().strftime("%B %-d, %Y"),
        help='defaults to today in "Month D, YYYY" format',
    )
    c.add_argument(
        "--name",
        default=_default_name(),
        help="defaults to user_profile.json contact.name",
    )
    c.add_argument(
        "--contact",
        default=_default_contact_line(),
        help="defaults to 'email | phone | linkedin [| github]' from user_profile.json",
    )
    c.add_argument("--pdf", required=True, type=Path, help="output pdf path")
    c.add_argument("--keep-html", action="store_true", help="also save the intermediate .html beside the PDF (debug)")
    return p


def main() -> None:
    args = build_parser().parse_args()
    if args.cmd == "resume":
        render_resume(args.input, args.pdf, keep_html=args.keep_html)
    elif args.cmd == "cover-letter":
        render_cover_letter(
            body_path=args.body,
            out_pdf=args.pdf,
            company=args.company,
            salutation=args.salutation,
            date_str=args.date,
            name=args.name,
            contact=args.contact,
            keep_html=args.keep_html,
        )


if __name__ == "__main__":
    main()

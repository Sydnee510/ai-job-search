# Example resume template

This folder contains a **generic example resume** that shows what `.claude/skills/ai-job-apply/render_pdf.py` produces when you run it against a well-formed resume markdown file.

## Files

- `example_resume.md` — a fictional candidate ("Jordan Taylor Chen") in the exact markdown format `render_pdf.py resume` expects. Use this as a structural reference for how to lay out section headers, entry lines, and bullets in your own `knowledge/master_resume.md`.
- `example_resume.pdf` — (generated, not committed by default) the rendered PDF. Regenerate with the command below any time you tweak the template or the markdown.

## Regenerate the example PDF

From the project root:

```bash
python3 .claude/skills/ai-job-apply/render_pdf.py resume \
  --input example-resume-template/example_resume.md \
  --pdf   example-resume-template/example_resume.pdf
```

The rendered PDF uses the blue brand color (`#1E40AF`) from `knowledge/templates/resume.html`. Change the `--brand-accent` value in that template to recolor the whole system.

## Using this as a structural reference

When you edit `knowledge/master_resume.md` with your own content, follow `example_resume.md`'s structure exactly:

- `# Name` as the first line (renderer uses `user_profile.contact.name` in tailored resumes, but the manual structure must still match)
- Contact line on the second line (`email | phone | linkedin | github`)
- `## Professional Summary` → one paragraph
- `## Work Experience` → `### Company — Location` then `**Role** · dates` then bullets
- `## Technical Projects` → `### Project Name` optional subtitle, then bullets
- `## Volunteer Community Involvement` → `### Org: Role · dates` then bullets
- `## Skills` → category-prefixed bullet list
- `## Education` → bullet list

The em-dash in `### Company — Location` is a structural parser token, not prose — see `knowledge/writing_voice.md` for the full rule.

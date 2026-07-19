# Skill Authoring Guidelines

This repository stores personal skills under `skills/<skill-name>/`.

## Skill Layout

Every published skill must include:

```text
skills/<skill-name>/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
├── references/
└── assets/
```

Only create resource directories that the skill actually uses. Keep skill folders portable: another agent should be able to copy `skills/<skill-name>/` into a client skill directory and use it directly.

## Root Directory Roles

- `skills/`: published skills.
- `incubator/`: drafts and experiments that should not be installed by default.
- `templates/`: reusable scaffolds for new skills.
- `scripts/`: repository-level maintenance tools.
- `docs/`: human-facing notes, plans, history, and authoring conventions.

## Writing Rules

- Keep `SKILL.md` concise and procedural.
- Put detailed domain notes in `references/`.
- Put deterministic helper code in `scripts/`.
- Put reusable files and templates in `assets/`.
- Do not add `README.md`, changelogs, or long project history inside an individual skill bundle.
- Keep skill names lowercase with hyphen-separated words.

## Validation

Run this before committing:

```bash
python3 scripts/validate_all_skills.py
python3 -m unittest discover tests
```

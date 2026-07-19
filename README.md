# Own Skills

Personal Agent Skills for recurring work in Codex and other Agent Skills-compatible clients.

## Repository Layout

```text
.
├── skills/       # Published, installable skills
├── incubator/    # Draft skills and experiments
├── templates/    # Reusable scaffolds for new skills
├── scripts/      # Repository-level maintenance tools
└── docs/         # Authoring notes and history
```

## Included Skills

- `read-algorithm-repos`: Analyze algorithm repositories and Repomix artifacts, producing architecture maps, pipeline reports, core model inventories, code navigation, and newcomer onboarding material.

## Install A Skill

From this repository root:

```bash
python3 scripts/install_skill.py read-algorithm-repos --client codex --scope user --dry-run
python3 scripts/install_skill.py read-algorithm-repos --client codex --scope user
```

Supported clients are `codex`, `claude-code`, `opencode`, and `agents`. Use `--scope project --project-root <path>` for project-local installation.

You can also install a skill by copying `skills/<skill-name>/` into the target client's skills directory.

## Validate

Validate every published skill:

```bash
python3 scripts/validate_all_skills.py
```

Run all tests:

```bash
python3 -m unittest discover tests
```

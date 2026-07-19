# Read Algorithm Repositories V2.1 Implementation Plan

**Goal:** Make Repomix bootstrap automatically through `npx` and make generated reports function as a newcomer-oriented architecture learning tool.

**Architecture:** Keep Repomix preparation deterministic in `prepare_repomix.py`, enrich the shared analysis manifest with learning semantics, and make Markdown/HTML consume the same evidence. Extend validation so reduced search filters or missing newcomer guidance fail before delivery.

**Tech stack:** Python 3.9+, JSON Schema, Markdown, self-contained Vanilla HTML/CSS/JS.

## Tasks

- [ ] Add failing tests for local Repomix, automatic `npx`, `--no-download`, and generation failure evidence.
- [ ] Implement cross-platform `npx` discovery, automatic download execution, timeout, and provenance fields.
- [ ] Extend the manifest contract with model families, learning metadata, relationships, entry points, and modification guidance.
- [ ] Upgrade the architecture and HTML contracts around newcomer questions, progressive disclosure, rich filters, sorting, and core-only defaults.
- [ ] Extend report validation for required newcomer sections, code-index semantics, filter controls, and snapshot provenance.
- [ ] Validate the Skill bundle, install it to the personal Skill directory, and run the complete DeepCTR-Torch workflow.
- [ ] Validate Markdown/Manifest/HTML and exercise both required desktop browser viewports.

## Acceptance

- A missing Repomix executable selects `npx --yes repomix` by default.
- `--no-download` prevents network bootstrap and produces an explicit fallback reason.
- Markdown explains the mental model, model families, source learning route, and safe modification points.
- HTML exposes category, stage, Symbol kind, model family, importance, learning phase, path root, core-only, sorting, counts, and reset.
- Both reports retain exact repository-relative source anchors and agree with the same manifest.

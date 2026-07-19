---
name: read-algorithm-repos
description: Use when analyzing an algorithm repository or packed Repomix artifact for architecture, industrial pipeline mapping, core model inventory, newcomer onboarding, source navigation, or a model/module deep dive; applies to recommendation, ads, search, NLP, CV, graph, RL, and generic machine-learning codebases, including requests phrased as reading an 算法代码仓.
compatibility: Requires local file access. Shell and Python 3.9+ enable deterministic helpers; Git, Repomix, and browser automation are optional. Designed for Codex, Claude Code, OpenCode, and Agent Skills-compatible clients on macOS, Windows, and Linux.
metadata:
  version: "2.1.0"
  portability: "agent-skills-open-standard"
---

# Read Algorithm Repositories

## Core Principle

Act as a senior algorithm architect reading source for a new engineer. Build a noise-reduced map first, identify the domain, map files to the correct industrial pipeline, and deep-read only the source needed to explain data flow and representative models. Never list a model without a repository-relative source path when code is available.

## Entry Modes

- **Repository architecture**: architecture, pipeline, model atlas, Markdown/HTML onboarding report.
- **Module deep dive**: one model, layer, `forward()` path, paper block, tensor flow, or modification point.
- **Local checkout**: Repomix-first mapping followed by line-accurate local source verification.
- **Packed-only**: a provided Repomix XML/Markdown/JSON artifact is the primary corpus; disclose that current local paths and lines cannot be verified.

## Portable Runtime Contract

1. Resolve every bundled path relative to the directory containing this `SKILL.md`; never rely on a client-specific variable or current working directory.
2. Detect capabilities before work: local filesystem, shell, Python, Git, local Repomix executable, and browser automation.
3. For repository-level analysis, automatically bootstrap Repomix through an existing `npx`/`npx.cmd` when no local or global Repomix executable exists. This is an intentional default of this Skill; host permission prompts still apply. Use `--no-download` only when the user requests offline/restricted operation or the environment forbids network access. Never auto-download unrelated counters, browsers, libraries, or editor helpers.
4. Choose the strongest available QA level:
   - `browser`: static validation plus real browser interaction and desktop viewport checks.
   - `static`: bundled validators only; state that visual browser QA was not executed.
   - `disclosed-only`: manual structural checks; name every skipped deterministic check.
5. Treat `agents/openai.yaml` as optional Codex UI metadata. It is not part of the analysis contract.
6. To copy this bundle into another supported CLI discovery directory, inspect `python <skill-root>/scripts/install_skill.py --help`, run with `--dry-run` first, and never replace an existing installation without explicit approval.

## Repository Workflow

### 1. Prepare a repository map

For every local repository-level read, follow `references/repomix-local-workflow.md`.

- With Python, run `<skill-root>/scripts/prepare_repomix.py --repo <repo-root> --execute` before broad source analysis. It reuses a fresh artifact, prefers project-local/global Repomix, and otherwise runs `npx --yes repomix@latest` cross-platform.
- Use `--no-download` only for an explicit offline/restricted request. If bootstrap fails, preserve the exact execution source/error, continue with the filtered tree and Symbol map, and describe the failure rather than saying only “Repomix unavailable.”
- Use the artifact tree, metadata, and targeted file sections for global mapping. Do not inject the entire pack into context by default.
- When Repomix is unavailable, use a filtered tree and Symbol map, record the fallback, and continue.

### 2. Collect deterministic evidence

When Python is available, run:

```text
python <skill-root>/scripts/collect_repo_stats.py --repo <repo-root> --config <skill-root>/assets/repomix-base.config.json --output <work-dir>/repo-stats.json
python <skill-root>/scripts/build_code_index.py --repo <repo-root> --config <skill-root>/assets/repomix-base.config.json --output <work-dir>/code-index.json
```

- Statistics use a declared metric and the same noise boundary as the map.
- The code index is repository-relative first. Absolute paths and IDE URIs are machine-local enhancements only.
- Return to local source for representative implementations, current line numbers, behavior, tests, and ambiguous boundaries. Local source wins over the packed snapshot.
- If Python is unavailable, reproduce the same fields with available structured tools and disclose the fallback method.

### 3. Identify the domain and industrial pipeline

Support the classification with README/docs, manifests, examples, module names, classes, and representative source.

- Recommendation/ads: offline data & features -> match/recall -> pre-ranking -> ranking -> reranking/business policy.
- Search: offline documents & indexing -> query analysis -> recall -> pre-ranking -> ranking -> reranking.
- NLP/CV/graph/RL/generic ML: data input & preprocessing -> core model/modules -> training/evaluation/inference.

For every stage, label coverage as `full`, `partial`, `inferred`, `external`, or `absent`. Do not turn a model name into proof that an industrial stage is implemented.

### 4. Build the shared analysis manifest

Before rendering repository-level Markdown or HTML, synthesize `algorithm-repo-analysis.json` using `assets/analysis-manifest.schema.json` and the measured statistics/code index.

The manifest is the shared source for:

- repository revision, snapshot status, exclusions, and runtime capabilities;
- domain evidence and one-sentence framing;
- language/line statistics and role scale;
- ordered pipeline stages, coverage, inputs/outputs, logic, and source anchors;
- offline, online, and representative model flows;
- code index, core model inventory, strengths, limitations, production gaps, and reading order;
- newcomer mental model, key concepts, entry points, learning tracks, modification guide, model families, importance, and source relationships.

For a non-trivial code index, enrich deterministic entries with `stage`, `modelFamily`, `importance`, `learningPhase`, `summary`, and `tags`. Keep all Symbols searchable, but designate a smaller architecture-core subset so newcomers are not dropped into an undifferentiated method dump.

Keep uncertain claims explicit. Use `null`, `inferred`, `external`, or `absent` rather than invented precision.

### 5. Render requested artifacts

- Architecture report: follow `references/architecture-report-template.md`.
- Module deep dive: follow `references/module-deep-dive-template.md`.
- HTML report: also follow `references/html-experience-design.md`.
- Source navigation: follow `references/html-code-navigation.md`.

When Python is available, render the default self-contained HTML cockpit deterministically:

```text
python <skill-root>/scripts/render_html_report.py --manifest <manifest.json> --output <report.html>
```

Customize the renderer only when repository-specific topology cannot be expressed by the V2.1 Manifest. Preserve all required control IDs and rerun validation after customization.

Repository-level Markdown uses validated Mermaid for offline, online, and representative model flows by default. HTML translates the same manifest nodes and edges into self-contained native HTML/CSS diagrams; it must not parse Markdown as its only data source.

Render for progressive learning: orientation first, shared abstractions second, representative model families third, training/validation fourth, and production gaps last. Every core model must answer what problem it solves, how its structure works, which shared layers it reuses, where an example starts, which test confirms behavior, and why a newcomer should study it.

### 6. Validate before delivery

When Python is available, run:

```text
python <skill-root>/scripts/validate_reports.py --manifest <manifest.json> --markdown <report.md> --html <report.html>
```

- Fix all validator errors.
- At `browser` QA level, open the actual HTML and complete the desktop checks in `references/html-experience-design.md` at `1440 x 900` and `1280 x 720`.
- At `static` or `disclosed-only` level, do not claim browser verification. Report exactly what was validated.

## Repository Deliverable Checklist

- One-sentence architect framing with evidence.
- Tech stack, primary language, measured language/line distribution, role scale, method, and exclusions.
- Repomix snapshot decision and freshness basis.
- Pipeline mapping with paths, Symbols, coverage, and implementation logic.
- Core model/layer/data/trainer/example/test inventory with repository-relative paths.
- Newcomer mental model, key concepts, at least one ordered reading track, and a “where to modify” guide grounded in source.
- Model-family atlas with problem, architecture, prerequisites, shared layers, examples, tests, and learning value.
- Mermaid offline/online/model flow in Markdown and equivalent visual HTML flows.
- Searchable HTML model atlas and Code Map when the index is non-trivial. The Code Map must expose category, pipeline stage, Symbol kind, model family, importance, learning phase, path root, core-only mode, sorting, counts, active filters, and one-action reset.
- Source navigation that is honest about static-browser limits and portable across operating systems.
- Strengths, limitations, production gaps, and newcomer reading order.
- Shared manifest and QA level so Markdown and HTML cannot silently drift.

## Module Deliverable Checklist

- Math or paper concept mapped to exact code.
- Tensor shape flow through `forward()` or equivalent.
- Core framework operators and why they are used.
- Bottlenecks, edge cases, OOM risks, and safe modification points.

## Quality Bar

- Be useful to an engineer joining the project tomorrow.
- Prefer code-grounded explanations over paper-only summaries.
- Prefer map-first targeted reading over exhaustive file-by-file scanning.
- Call out missing industrial stages as clearly as implemented ones.
- Keep the report, manifest, paths, line numbers, and diagrams mutually consistent.

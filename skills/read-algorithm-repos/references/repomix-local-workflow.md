# Repomix-First Local Repository Workflow

Use this workflow for repository-level architecture analysis when a local checkout is available. Repomix is the noise-reduced architecture map; the local checkout is the final source of truth.

## Contents

1. Decision contract
2. Inspect the checkout
3. Check snapshot freshness
4. Generate a noise-reduced snapshot
5. Build the global map
6. Select deep-read targets
7. Verify against local source
8. Token discipline
9. Common mistakes
10. Completion contract

## 1. Decision Contract

| Situation | Required behavior |
|---|---|
| Local checkout, repository-level report | Use Repomix first, then targeted local source reading |
| Fresh Repomix artifact exists | Reuse it for mapping |
| Repomix artifact is absent or stale | Regenerate before broad architecture analysis; bootstrap through `npx` when needed |
| Only a packed artifact is available | Use it as the primary corpus and state that local line verification is unavailable |
| User requests one explicit model/file deep dive | Read the target and direct dependencies; repository-wide regeneration is optional |
| No local/global Repomix, but `npx` exists | Run `npx --yes repomix@latest` automatically and record `executionSource: npx-download` |
| Repomix bootstrap is blocked or fails | Record the exact command source/error, then continue with filtered tree/Symbol map |
| User explicitly requests offline operation | Pass `--no-download`; never attempt network access |

Do not begin by opening many source files. Establish the map and relevance boundary first.

## 2. Inspect the Checkout

Perform a cheap metadata pass without reading file contents broadly:

- Locate repository root and current Git state when available.
- Look for `repomix-output.xml`, `repomix-output.md`, `repomix-output.json`, or project-specific packed artifacts.
- Identify source roots, examples, tests, manifests, training configs, serving configs, and generated/output directories.
- Check whether Repomix is already available as a project dependency or global command, then whether `npx`/`npx.cmd` can bootstrap it.
- Do not let an existing packed artifact include itself recursively.

This pass may inspect names, sizes, timestamps, and Git metadata. It should not become an exhaustive content scan.

## 3. Check Snapshot Freshness

Do not treat a packed artifact as current merely because it exists.

Use the strongest available evidence:

1. Read Repomix metadata or generation timestamp when present.
2. Compare artifact modification time with the latest relevant Git commit.
3. Check uncommitted source, manifest, example, test, and architecture-relevant config files.
4. If any relevant tracked or untracked file is newer than the artifact, treat the artifact as stale.
5. If freshness cannot be established confidently, regenerate.

Ignore newer files that are already excluded noise, such as logs, caches, datasets, weights, checkpoints, and generated reports.

Record the decision internally:

```text
Repomix: reused | regenerated | unavailable
Freshness basis: metadata | Git commit + working tree | file timestamps
Artifact: path/to/repomix-output.xml
```

## 4. Generate a Noise-Reduced Snapshot

Use the bundled, versioned base configuration at `assets/repomix-base.config.json`. Resolve it from the Skill root, not the current working directory. Inspect first:

```text
python <skill-root>/scripts/prepare_repomix.py --repo <repo-root>
```

For repository-level analysis, invoke preparation with execution enabled:

```text
python <skill-root>/scripts/prepare_repomix.py --repo <repo-root> --execute
```

The helper follows this order:

1. Reuse a fresh artifact.
2. Use `<repo>/node_modules/.bin/repomix` when available.
3. Use a global `repomix` command when available.
4. Use cross-platform `npx --yes repomix@latest` when neither exists.
5. Fall back only when Repomix generation fails, `npx` is unavailable, or downloading is disabled.

Use `--no-download` for explicit offline/restricted execution. The helper has a bounded timeout and records `executionSource`, `downloadPolicy`, package spec, and the concrete error. Host sandbox/network approval prompts remain authoritative. Adapt a copied working config only when the base patterns would remove architecture-relevant content; record every material override.

Keep these by default:

- README and architecture documentation.
- Source code, examples, and tests.
- Dependency/build manifests such as `pyproject.toml`, `setup.py`, package manifests, and requirements files.
- Model, data, training, evaluation, export, and serving configuration.
- Dockerfiles, entrypoints, and CI workflows when they reveal runtime or validation behavior.
- Small schemas and fixtures needed to understand input/output contracts.

Do not globally exclude YAML, TOML, JSON, shell scripts, or all configuration files. They often contain the training and serving architecture.

## 5. Build the Global Map

Use the packed artifact in layers. Do not inject the complete artifact into context by default.

1. Read repository metadata and the packed file tree.
2. Identify languages, frameworks, manifests, entrypoints, source roots, examples, and tests.
3. Search file paths and declarations for datasets, features, encoders, models, layers, losses, trainers, evaluators, inference, export, serving, indexes, retrieval, ranking, and policy.
4. Classify the domain from code-backed evidence.
5. Choose the industrial pipeline and map directories/files to stages.
6. Mark covered, partially covered, inferred, external, and absent stages separately.
7. Produce a shortlist of files and Symbols that require local deep reading.
8. Collect language and code-volume statistics from the same fresh snapshot and exclusion boundary used for the map.

Repomix answers “where is the architecture?” It is not the final evidence for every implementation claim.

### Language and Code-Volume Statistics

For repository-level reports, measure rather than infer engineering scale. Use the bundled counter as the portable baseline:

```text
python <skill-root>/scripts/collect_repo_stats.py --repo <repo-root> --config <skill-root>/assets/repomix-base.config.json --output <work-dir>/repo-stats.json
```

It groups recognized source extensions, counts non-empty physical lines, and breaks down roles such as models, shared layers/operators, data/input, training/evaluation/inference, examples, and tests. Label the metric exactly; it is not semantic code lines. A fresh Repomix summary or an already-installed `cloc`, `scc`, or `tokei` may be added as secondary evidence, but must not silently replace the manifest metric. Record method, revision, and exclusions. Do not install a counter silently.

Use the same noise rules as the Repomix artifact. Keep generated/vendor code separate so it cannot distort the primary implementation language.

## 6. Select Deep-Read Targets

Read local source in priority order:

1. Public API exports and executable entrypoints.
2. Shared model/base classes and feature/input abstractions.
3. Dataset, preprocessing, trainer, evaluator, inference, and serving paths.
4. One representative model per meaningful model family.
5. Shared layers/operators used across those models.
6. Examples that show end-to-end assembly.
7. Tests that define shapes, errors, defaults, and supported behavior.

Expand only when a claim, dependency, or pipeline boundary remains unresolved. Do not read every model body merely to prove the model file exists.

## 7. Verify Against Local Source

Use the checkout for:

- Current file existence and repository-relative paths.
- Class/function declarations and line numbers.
- AST/Symbol extraction and exported model counts.
- Representative `forward()`, training, evaluation, and inference behavior.
- Claims that the Repomix snapshot omits or summarizes ambiguously.
- Detection of local changes made after the snapshot.

When Repomix and local source differ, local source wins. Regenerate the artifact when the difference affects the architecture map.

For HTML reports, build the Code Map from local paths and Symbols whenever the checkout is available. Do not derive absolute paths or IDE links from packed text alone.

## 8. Token Discipline

- Read the tree before file bodies.
- Search the packed artifact before extracting sections.
- Extract selected `<file path=...>` blocks instead of the entire XML.
- Deep-read shared abstractions and representative models before repetitive siblings.
- Use AST or structured parsers for inventories and line numbers.
- Reuse the architecture map across Markdown and HTML, but build HTML source navigation from the local code index.
- Build `algorithm-repo-analysis.json` before rendering either report; both artifacts consume its ordered stages, flows, statistics, and source anchors.
- Stop expanding context once every report claim has a code anchor and unresolved boundaries are explicit.

## 9. Common Mistakes

| Mistake | Correct behavior |
|---|---|
| Scan the checkout file by file before mapping | Build the Repomix map first |
| Load the whole XML because it is one file | Search and extract only relevant sections |
| Trust an old artifact | Check freshness or regenerate |
| Exclude all configs and tests | Keep architecture-relevant configs and behavioral tests |
| Use Repomix line positions as source line numbers | Resolve lines from local files |
| Treat a model name as proof of pipeline coverage | Read representative implementation and entry flow |
| Skip Repomix merely because it is not installed | Let the helper bootstrap through `npx`; honor host permissions and `--no-download` |
| Let generated reports enter the next snapshot | Exclude outputs and existing Repomix artifacts |

## 10. Completion Contract

A local repository architecture read is ready for reporting only when:

- [ ] Repomix was reused, regenerated, or explicitly unavailable.
- [ ] Missing local Repomix triggered `npx` unless offline/restricted mode was explicit.
- [ ] Bootstrap source, download policy, and any error were recorded precisely.
- [ ] Freshness and exclusion scope were checked.
- [ ] Domain and pipeline were derived from the packed map.
- [ ] Deep-read targets were selected from that map.
- [ ] Repository-level reports include measured language/code-volume statistics, method, and exclusions.
- [ ] Key implementation claims were verified in local source.
- [ ] Paths, Symbols, and line numbers came from the current checkout.
- [ ] Missing industrial stages were distinguished from uninspected stages.
- [ ] `algorithm-repo-analysis.json` conforms to `assets/analysis-manifest.schema.json`.
- [ ] Markdown and HTML were rendered from the same manifest and share the same architecture conclusions.

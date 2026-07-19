# HTML Code Navigation

Use this when generating HTML reports that should navigate to source files, folders, IDEs, or local code locations.

## Source of Truth

HTML must not be generated only from the Markdown report. Before rendering navigation, build a code index from the local checkout or Repomix context:

| Field | Meaning | How to discover |
|---|---|---|
| `relativePath` | Repo-relative path shown to readers | `rg --files`, Repomix `<file path=...>` |
| `absolutePath` | Optional machine-local path | join repo root + relative path on the current platform |
| `symbol` | Class/function/model name | `rg "^class |^def |def forward"` or language equivalent |
| `line` | Best-effort 1-based line number | `rg -n`, AST parser, or source grep |
| `stage` | Pipeline stage | domain mapping |
| `category` | model/layer/example/trainer/test | file path and class role |
| `language` | Implementation language | extension mapping |
| `pathRoot` | Top-level source root | first repository-relative path segment |
| `modelFamily` | Architecture family when applicable | architect-curated model atlas |
| `importance` | core/important/supporting/reference | architecture significance |
| `learningPhase` | orientation/foundation/model-deep-dive/training-validation/production | newcomer reading order |
| `summary`, `tags` | Responsibility and searchable concepts | targeted source analysis |

Expose this index in the HTML as model cards, path chips, pipeline nodes, and/or a searchable Code Map.

Keep deterministic metadata from `build_code_index.py`, then enrich stages, families, summaries, tags, and relationships through targeted source reading. Do not classify every method in a model file as `core`; reserve that label for public or representative architecture Symbols and use `important` for lifecycle boundaries.

## Static HTML Link Options

Static single-file HTML cannot execute shell commands. It can only navigate to URLs. Provide the best links available:

1. **Relative file link** when the HTML is saved inside the repo:
   ```html
   <a href="../deepctr_torch/models/deepfm.py">deepctr_torch/models/deepfm.py</a>
   ```
   This usually opens the source file in the browser as text. It is portable within the repo but does not reveal the file in the operating-system file manager and does not reliably jump to a line.

2. **Absolute `file://` link** when an absolute repo path is known. Generate it with `scripts/build_code_index.py`; do not concatenate URL strings by hand:
   ```html
   <a href="file:///current-platform/repo/deepctr_torch/models/deepfm.py">Open file</a>
   ```
   Browser behavior varies. It may open the file, block navigation, or show it as text.

3. **IDE deep link** when the user uses VS Code-compatible editors. Consume the generated `editorUri` field so drive letters, UNC paths, separators, spaces, and URI escaping follow the current platform:
   ```html
   <a href="vscode://file/current-platform/repo/deepctr_torch/models/deepfm.py:14:1">Open in VS Code</a>
   ```
   This can open a file at a line number if VS Code is installed and the browser allows the external protocol. Similar editor-specific protocols may exist, but do not assume them without user confirmation.

## Double-click Behavior

Use `dblclick` to open a preferred navigation target, but keep a normal click fallback:

```html
<span class="path-chip"
      data-relative="deepctr_torch/models/deepfm.py"
      data-file="GENERATED_FILE_URI"
      data-ide="GENERATED_EDITOR_URI">
  deepctr_torch/models/deepfm.py::DeepFM
</span>
<script>
  document.querySelectorAll('.path-chip').forEach(el => {
    el.addEventListener('click', () => navigator.clipboard?.writeText(el.textContent.trim()));
    el.addEventListener('dblclick', () => {
      window.location.href = el.dataset.ide || el.dataset.file;
    });
  });
</script>
```

## Platform-Neutral File and Folder Opening

Use this default user-facing copy:

> 单击复制源码定位信息；双击尝试通过已配置的 IDE 打开对应文件和行号。由于浏览器安全限制，纯静态 HTML 无法直接调用操作系统文件管理器或执行本地命令。

A pure static HTML file cannot execute local commands because browsers sandbox local files. It cannot reliably reveal a selected file in the operating-system file manager. To add that behavior, use one of these optional approaches only with the user's agreement:

### Option A: Local helper server

Generate HTML that calls a localhost endpoint on double-click. The user must run the helper separately.

```js
fetch('http://127.0.0.1:8765/reveal?path=' + encodeURIComponent(absPath));
```

The helper may use platform-specific commands:

- macOS Finder: `open -R /absolute/path/to/file.py`
- Windows File Explorer: `explorer /select,"C:\absolute\path\to\file.py"`
- Linux desktop file manager: `xdg-open /absolute/path/to/folder`
- VS Code-compatible editor: `code -g /absolute/path/to/file.py:14`

Only use this when the user explicitly accepts a non-static local helper. Validate paths are inside the repo root to avoid arbitrary command execution.

### Option B: Custom URL protocol

Use a registered protocol such as `repo-reader://open?path=...&line=...`. This requires installing a local app/protocol handler, so do not assume it exists.

### Option C: Copy command fallback

If no helper exists, copy repository-relative source coordinates by default. Platform-specific command examples may appear inside optional details only:

```text
path/to/file.py:14 :: SymbolName
```

## UX Requirements

- Show repo-relative paths by default; hide absolute paths in tooltips or secondary actions.
- Source `relativePath`, `fileUri`, and `editorUri` from the shared manifest/code index; never infer URI syntax in browser JavaScript.
- Keep every model/layer/table row linked to at least a relative file target when possible.
- If line numbers are known, include line-aware IDE links.
- Explain limitations in the HTML only when navigation features are present, briefly and without clutter.
- Keep default copy valid on macOS, Windows, and Linux. Platform-specific examples belong in optional details, not the primary navigation note.
- Never imply static HTML can reveal locations in an operating-system file manager without a helper.

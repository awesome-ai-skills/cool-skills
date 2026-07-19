# 自有技能库（Own Skills）

一套个人 Agent Skills 集合，用于在 Codex 及其他兼容 Agent Skills 的客户端中完成重复性工作。

## 仓库结构

```text
.
├── skills/       # 已发布、可安装的技能
├── incubator/    # 草稿技能与实验性内容
├── templates/    # 用于新建技能的可复用脚手架
├── scripts/      # 仓库级别的维护工具
└── docs/         # 编写说明与历史记录
```

## 已包含的技能

- `read-algorithm-repos`：分析算法仓库与 Repomix 产物，生成架构图、流水线报告、核心模型清单、代码导航以及新人上手材料。

## 安装技能

在本仓库根目录下执行安装脚本。推荐**先加 `--dry-run` 演习一遍**，确认目标路径无误后再正式安装。

### 各客户端示例

脚本支持四种客户端，安装位置如下（`--scope user` 为用户级，`~` 表示家目录）：

| 客户端 | `--client` 取值 | 用户级安装目录 |
|--------|----------------|----------------|
| Codex | `codex` | `~/.codex/skills/` |
| Claude Code | `claude-code` | `~/.claude/skills/` |
| OpenCode | `opencode` | `~/.config/opencode/skills/` |
| Agents | `agents` | `~/.agents/skills/` |

```bash
# Codex（先演习，再正式安装）
python3 scripts/install_skill.py read-algorithm-repos --client codex --scope user --dry-run
python3 scripts/install_skill.py read-algorithm-repos --client codex --scope user

# Claude Code
python3 scripts/install_skill.py read-algorithm-repos --client claude-code --scope user --dry-run
python3 scripts/install_skill.py read-algorithm-repos --client claude-code --scope user

# OpenCode
python3 scripts/install_skill.py read-algorithm-repos --client opencode --scope user --dry-run
python3 scripts/install_skill.py read-algorithm-repos --client opencode --scope user

# Agents
python3 scripts/install_skill.py read-algorithm-repos --client agents --scope user --dry-run
python3 scripts/install_skill.py read-algorithm-repos --client agents --scope user
```

想一次性装到所有客户端，用 `--client all` 即可（各客户端并行判断、互不中断）：

```bash
# 先演习，确认每个客户端的目标路径
python3 scripts/install_skill.py read-algorithm-repos --client all --scope user --dry-run
# 正式安装到全部客户端
python3 scripts/install_skill.py read-algorithm-repos --client all --scope user
```

### 常用参数

- `--client`：目标客户端，取值为 `codex`、`claude-code`、`opencode`、`agents` 之一，或 `all`（一次性安装到上述全部客户端）。
- `--dry-run`：**演习模式**。只打印"会安装到哪里、是否会覆盖已有目录"，不真正复制文件。建议正式安装前先跑一次确认路径。
- `--force`：目标目录已存在时，先删除再覆盖。不加此参数且目标已存在会报错中止。
- `--skip-missing`：若某客户端的技能根目录（如 `~/.codex/skills/`）原本就不存在，则**跳过该客户端、不替你新建目录**。常与 `--client all` 搭配，只装到本地确实安装了的 agent。
- `--scope`：安装范围，取值为 `user` 或 `project`，**都是固定关键字，不要替换成实际用户名**。`user` 表示装到当前用户的家目录（脚本通过 `Path.home()` 自动解析为如 `/Users/michael` 的真实路径，无需你手写）；`--scope project --project-root <path>` 则表示改为**项目级**安装，装到指定项目目录下对应客户端的 `skills/` 子目录。
- `--repository <path>`：指定本仓库根目录（默认自动取脚本所在位置的上一级）。

你也可以跳过脚本，直接将 `skills/<skill-name>/` 目录复制到上表中对应客户端的技能目录里完成安装。

## 校验

校验所有已发布的技能：

```bash
python3 scripts/validate_all_skills.py
```

运行全部测试：

```bash
python3 -m unittest discover tests
```

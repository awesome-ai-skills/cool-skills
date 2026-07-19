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

在本仓库根目录下执行：

```bash
python3 scripts/install_skill.py read-algorithm-repos --client codex --scope user --dry-run
python3 scripts/install_skill.py read-algorithm-repos --client codex --scope user
```

支持的客户端包括 `codex`、`claude-code`、`opencode` 和 `agents`。若要在项目本地安装，请使用 `--scope project --project-root <path>`。

你也可以直接将 `skills/<skill-name>/` 目录复制到目标客户端的技能目录中来完成安装。

## 校验

校验所有已发布的技能：

```bash
python3 scripts/validate_all_skills.py
```

运行全部测试：

```bash
python3 -m unittest discover tests
```

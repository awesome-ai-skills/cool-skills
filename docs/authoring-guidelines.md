# 技能编写规范

本仓库的个人技能存放在 `skills/<skill-name>/` 下。

## 技能布局

每个已发布的技能必须包含以下内容：

```text
skills/<skill-name>/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
├── references/
└── assets/
```

只创建技能真正会用到的资源目录。保持技能目录的可移植性：其他人应当能够把 `skills/<skill-name>/` 直接复制到某个客户端的技能目录中并立即使用。

## 根目录职责

- `skills/`：已发布的技能。
- `incubator/`：默认不应被安装的草稿与实验性内容。
- `templates/`：用于新建技能的可复用脚手架。
- `scripts/`：仓库级别的维护工具。
- `docs/`：面向人阅读的笔记、计划、历史记录以及编写约定。

## 编写规则

- 保持 `SKILL.md` 简洁且可操作（步骤化）。
- 把详细的领域知识放到 `references/` 中。
- 把确定性的辅助代码放到 `scripts/` 中。
- 把可复用的文件与模板放到 `assets/` 中。
- 不要在单个技能包里添加 `README.md`、变更日志或过长的项目历史。
- 技能名称一律使用小写字母、数字，并用连字符分隔单词。

## 校验

在提交之前运行以下命令：

```bash
python3 scripts/validate_all_skills.py
python3 -m unittest discover tests
```

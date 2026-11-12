# 技能目录

每个技能一个子目录：

```text
skills/
└── my-skill/
    ├── SKILL.md
    └── references/
        └── long-notes.md
```

## 新增技能

1. 新建 `skills/<name>/SKILL.md`，`name` 必须与目录名一致。
2. `description` 写清触发词、适用对象、能力摘要（至少 40 字符）。
3. 长资料放 `references/*.md`；它们只做链接检查，不强制 frontmatter。
4. 在根 `README.md` 和 `AGENTS.md` 里挂上入口。
5. 跑：

```bash
python tools/repo-kit/check_repo.py --root .
python tools/repo-kit/generate.py --root . --write
```

空白模板见 [SKILL.template.md](SKILL.template.md)（该文件不参与校验）。

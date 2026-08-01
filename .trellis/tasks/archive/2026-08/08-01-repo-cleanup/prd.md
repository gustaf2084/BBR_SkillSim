# 清理仓库非必要文件

## 目标

GitHub 仓库只保留必要项目内容,移除参考资料与临时文件。

## 范围

- `src/docs/汉化参考/`(56 文件):git rm --cached + .gitignore,本地保留
- `src/docs/*.xlsx`(2 文件):同上
- `_ui_shots/_crop_purity.png`:删除
- `screenshot_ui.py`:删除
- `.agents/`、`AGENTS.md`:加入 .gitignore(trellis 本地文件,不入库)
- 其余全部保留

## 约束

- 不重写 git 历史;不 force-push
- 本地文件除明确删除项外全部保留(--cached 模式)
- 不影响 CI、源码、运行时

## 验收

- [ ] 仓库已跟踪文件减少 ~60 个
- [ ] git status 干净(除历史遗留)
- [ ] ruff + pytest 不受影响(无代码改动,基线确认)
- [ ] CI 绿

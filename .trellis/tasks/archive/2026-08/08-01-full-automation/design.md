# 设计:全自动化机制

## A. 提交后自动推送 —— git post-commit hook

**方案**:仓库内 `.githooks/post-commit`(可入库)+ `git config core.hooksPath .githooks` 一条命令启用。

**hook 逻辑**:
```sh
#!/bin/sh
# 跳过:rebase 进行中、非 main 分支、不是本地分支提交(如 fast-forward)
[ -d .git/rebase-merge ] && exit 0
[ -d .git/rebase-apply ] && exit 0
branch=$(git symbolic-ref --short HEAD 2>/dev/null) || exit 0
[ "$branch" = "main" ] || exit 0
# 推送;失败只提示,exit 0 不阻断提交流程
git push origin main 2>&1 | sed 's/^/[auto-push] /' || echo "[auto-push] 推送失败,请手动 git push"
exit 0
```

**安全点**:
- rebase 检测:`.git/rebase-merge` 与 `.git/rebase-apply` 存在即跳过(rebase 会逐 commit 触发 post-commit)
- 非 main 分支跳过(避免把实验分支推上去)
- push 失败 exit 0(提交仍成功,仅提示)—— 与项目"不 force-push"原则一致
- Windows Git Bash 兼容:sh 脚本,git bash 自带

**启用方式**:`git config core.hooksPath .githooks`(本地配置,不进仓库)。提供 `scripts/` 说明或 CLAUDE.md 命令。注意 `git commit` 在 clone 新仓库后需要执行一次启用命令;hook 文件本身入库。

**备选被否**:Claude Code PostToolUse hook —— 只覆盖 AI 提交,用户手动 commit 不触发;`.git/hooks` 直接放 —— 不入库,clone 丢失。

## B. build.yml 自动发布

在现有 build + package 步骤后追加:

```yaml
- name: Publish Release
  uses: softprops/action-gh-release@v2
  with:
    files: release/BBR_SkillSimulator-v*.zip
    generate_release_notes: true        # 自动从提交生成说明
    draft: false
    prerelease: false
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

同时调整 Package artifacts 步骤的 zip 命名:现状是 `cp` 散文件;改为统一打 zip(脚本或 PowerShell `Compress-Archive`):
- 目录结构:zip 内 = `BBR_SkillSimulator.exe` + `data.json` + `perk_trees.json` + `perk_i18n.json` + `VERSION` + `icons/`(与 README "首次运行提示"一致)
- 文件名:`BBR_SkillSimulator-v${VER}.zip`
- `workflow_dispatch` 手动触发时:VER=dev-{sha},正常发布还是 v* 标签

**验证**:本地不能跑 GitHub Actions;语法用 actionlint 或 yaml 解析(项目无 actionlint —— 用 python yaml.safe_load 验证语法 + 人工审查步骤;更可靠的是推送 v 测试标签?不行,会触发真实发布。做法:推送前用 `python -c yaml.safe_load` 校验;发布到 GitHub 后在 workflow_dispatch 或下个真实标签验证)。

**风险**:softprops/action-gh-release 需要 tag 存在(push tags 触发时存在);重复跑同一 tag 会更新 release —— 幂等。

## C. CLAUDE.md 自动化约定

CLAUDE.md 新增 "自动化工作流(默认)" 节:

- 收到开发需求 → 默认全自动:建 Trellis 任务 → PRD/design/implement → review 关键决策点 → start → 实现 → ruff/mypy/pytest → 提交 → 自动推送(hook)
- 仅在 4 种情况停下问:①任务创建许可(大任务)②需求歧义/关键决策 ③不可逆远程操作 ④review 门(提交前展示计划)
- 小改动(修文案、调样式)可跳过 Trellis 任务,直接改+提交+推送
- 与 .githooks/post-commit 的关系:AI 提交后由 hook 自动推送,不再手动跑 push_github.bat

## D. README 增强

- 顶部徽章:workflow badge(`https://github.com/gustaf2084/BBR_SkillSim/actions/workflows/test.yml/badge.svg`)、release badge(`https://img.shields.io/github/v/release/gustaf2084/BBR_SkillSim`)、license badge(现有 GPL-3.0)
- 新增节:项目结构(简述 src/ 模块)、开发文档链接(`src/docs/开发文档.md`)、如何发布新版本(打 v 标签→自动构建发布,不再手动)
- 截图区:占位(`_ui_shots/` 目录已存在,README 引用)
- topics 设置(需认证):给出 `gh repo edit gustaf2084/BBR_SkillSim --add-topic ...` 或 GitHub 网页路径指令

## 需认证的远程操作(交付 D 的限制)

设置 topics、修改仓库元数据需要 GitHub 认证(gh CLI / PAT)。当前环境无 gh、无 token:
- 本地全部工作(A/B/C/D-README)不受阻
- topics:README 或交付说明中给出 3 行指令;若用户提供 token,我全自动执行
- 历史 13 个 release 不动(规范未来);v0.0.3 空 tag 不动(历史遗留)

## 验证方案

- hook:本地 `git commit` 触发实测(用一个空提交测试后 reset 掉,或用 dummy 分支);rebase 场景实测
- build.yml:`python -c "import yaml; yaml.safe_load(open(...))"` 语法验证 + 步骤审查
- README/CLAUDE.md:人工审查 + 链接检查
- 最终:提交并推送到 GitHub,test.yml 自动跑验证 CI 仍绿

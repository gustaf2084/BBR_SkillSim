# 执行计划:全自动化与仓库整理

## 实施清单

- [ ] A1. 创建 `.githooks/post-commit`(rebase/非 main 跳过 + 自动 push + 失败提示不阻断)
- [ ] A2. 执行 `git config core.hooksPath .githooks` 启用;测试:普通 commit 自动推送;rebase 场景跳过(用 `git rebase` 一个提交实测)
- [ ] B1. 修改 `.github/workflows/build.yml`:Package artifacts 统一打 zip(`BBR_SkillSimulator-v{VER}.zip`,含 exe+数据+icons),追加 `softprops/action-gh-release` 发布步骤(generate_release_notes)
- [ ] B2. YAML 语法验证(`python -c yaml.safe_load`)
- [ ] C1. CLAUDE.md 新增"自动化工作流(默认)"节(全自动链路 + 4 种停问场景)
- [ ] D1. README 增强:徽章(test/release/license)、项目结构、发布流程说明、截图区、开发文档链接
- [ ] D2. 整理说明:topics 设置指令(认证不可用时写入交付说明,README 或任务 notes)
- [ ] 验证:hook 实测;yaml 语法;README/CLAUDE.md 链接检查
- [ ] 提交(2 个:工作提交 split)并确认 hook 自动推送生效

## 质量闸门

- hook 脚本 `sh -n` 语法检查 + 实机测试(普通提交/rebase/非 main)
- build.yml 结构审查:zip 内容与 README 首次运行说明一致;重复触发幂等
- CLAUDE.md/README 中文一致、无占位
- 产品代码零改动(git status 核对)

## 回滚点

- hook 有问题:`git config core.hooksPath` 改回默认(删配置即可),脚本可留
- build.yml 有问题:revert 提交,Release 自动发布不影响历史(只对未来标签生效)
- 全部为配置/文档改动,无代码回滚

## 验收映射

prd.md 验收标准 6 条,全部完成即交付。

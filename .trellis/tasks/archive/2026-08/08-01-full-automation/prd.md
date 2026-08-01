# 项目全自动化与 GitHub 仓库整理

## 目标

让 BBR_SkillSim 达到"全自动":提交后自动推 GitHub、打版本标签后自动构建并发布 Release、会话内开发全自动(建任务→实现→提交→推送不打断)、GitHub 仓库整理规范。

## 需求(4 个交付物)

### A. 提交后自动推送
- git 提交成功后自动 push 到 origin/main(用户手动 commit 也生效,不依赖 push_github.bat)
- 必须安全:rebase 过程中不触发;非 main 分支不推;push 失败只提示不阻断 commit

### B. 自动构建 + 发布 Release
- 现有 `build.yml` 已能构建并打包 zip,但只 `upload-artifact`,**不创建 Release**(现状:13 个 release 全是手动上传)
- 增强:v* 标签推送 → 构建 → 自动创建/更新 GitHub Release 并挂载 zip 资产
- 资产命名统一:`BBR_SkillSimulator-v{VER}.zip`(现状点号分隔不一致)
- 发布说明从 changelog 自动生成(`src/docs/开发文档.md` 版本历史节)或提交信息摘要

### C. 会话内开发全自动约定
- 在 CLAUDE.md 中明确:收到开发需求默认全自动执行 Trellis 流程(建任务→PRD→实现→测试→提交→推送),仅在真正需要决策时询问
- 与 A 的 hook 配合:提交即推送,无需手动

### D. GitHub 仓库整理
- README 增强:CI/Release 徽章、项目结构、截图区、开发文档链接
- 设置 topics(需 GitHub 认证 —— 认证不可用时给出可执行指令)
- 规范说明:今后版本发布走"打 v 标签 → 自动发布",不再手动传 zip

## 范围

- **改动文件**:`.github/workflows/build.yml`、`README.md`、`CLAUDE.md`、新增 `.githooks/post-commit`、`docs/开发文档.md`(发布流程说明,如合适)
- **需认证的远程操作**:设置 topics、清理/重命名历史 release(不可用时只给指令,不阻塞其他交付物)
- **不在范围**:产品源码与测试零改动;不改动已有的 13 个 releases 与 15 个 tags(只规范未来)

## 约束

- 不 force-push;push 失败不静默(提示用户处理)
- hook 必须可入库(.githooks/ 入库 + core.hooksPath 配置),clone 后一条命令启用
- 概率引擎/UI 逻辑完全不触碰

## 验收标准

- [ ] A:提交后自动推送生效(main 分支);rebase 场景不误触;push 失败提示不阻断;`.githooks/post-commit` 已入库
- [ ] B:build.yml 含 Release 创建步骤(zip 自动上传);资产命名 `BBR_SkillSimulator-v{VER}.zip`
- [ ] C:CLAUDE.md 含"自动化工作流"约定节,描述全自动执行链路
- [ ] D:README 含徽章/结构/截图区;topics 设置指令文档化(若无法认证)
- [ ] 产品源码、tests 零改动;CI 工作流语法有效(本地能验证的部分已验证)
- [ ] 全部改动已提交并推送

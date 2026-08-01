# 交付说明与待办(需用户操作)

## 已完成(已推送)

- [x] `.githooks/post-commit` 自动推送 hook(rebase/非 main 跳过;61daf57 已实测)
- [x] `build.yml` 自动发布 Release:zip 统一命名 `BBR_SkillSimulator-v{VER}.zip` + action-gh-release
- [x] CLAUDE.md 自动化工作流约定(本地文件,不入库 —— .gitignore 既有决定)
- [x] README 增强:CI/Release/License 徽章、界面截图(10 张入库)、zip 下载说明、发布流程、GPL-3.0
- [x] test.yml 失败诊断:失败时上传 pytest 详细输出 artifact

## 待办:GitHub topics(需认证,本地无 token)

设置仓库主题标签,让仓库可被搜索:

```bash
# 方式 1:gh CLI(需先 gh auth login)
gh repo edit gustaf2084/BBR_SkillSim --add-topic battle-brothers,modding,probability,pyqt6,pyside6

# 方式 2:网页操作
# 仓库主页 → About 栏 → 齿轮图标 → Topics 输入: battle-brothers modding probability pyqt6 pyside6
```

## 可选(用户决定)

- 历史 13 个 release 资产命名不统一(`BBR_SkillSimulator.0.4.7.zip` 点号分隔)—— 已决定不动(规范未来);若想统一,需在 GitHub 逐个编辑 release
- `v0.0.3` 有 tag 无 release —— 历史遗留,不动

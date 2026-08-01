# 用 Trellis 规范 BBR_SkillSim 项目

## 目标

把 `.trellis/spec/` 从模板占位填充为 BBR_SkillSim 的真实编码规范,全部基于代码库证据(CLAUDE.md、源码、测试、`src/docs/开发文档.md`),删除不适用的模板部分。规范文档用中文书写。

## 范围

- **Spec 目录**:
  - 新建 `.trellis/spec/model/`(非 UI 层:engine、data_loader、app_paths、build_parser、perk_zh 等)
  - 新建 `.trellis/spec/view/`(UI 层:main_window、四个 tab、skill_tree_widget、ui_components、theme、i18n、icon_provider)
  - 更新 `.trellis/spec/guides/`(code-reuse、cross-layer 填充项目实例)
  - 删除 `.trellis/spec/backend/` 整个目录(含 database-guidelines、logging-guidelines 等不适用模板)
- **需检查的源**:`src/` 全部 16 个 .py、`tests/` 7 个测试文件、根 `CLAUDE.md`、`src/docs/开发文档.md`、`conftest.py`
- **不在范围内**:
  - 不修改任何产品源码、测试、CLAUDE.md、README、开发文档.md、VERSION
  - 不修改 `.trellis/` 除 `spec/` 以外的任何内容(hooks、agents、config、scripts)

## 架构背景(仓库分析结论)

- 单包 Python 桌面应用:`src/` 内 16 个模块,Model/View 分层清晰
- **Model 层**:`engine.py`(概率核心,6 个实例级缓存、非线程安全、analytic/Monte Carlo 双模式)、`data_loader.py`(GameData 加载后只读、双语访问器、settings.json 持久化、UI 背景过滤)、`app_paths.py`(PyInstaller 路径)、`build_parser.py`、`perk_zh.py`
- **View 层**:`main_window.py`(导航 + 四 tab)、`tab_forward/tab_reverse/tab_builds/tab_about.py`、`skill_tree_widget.py`(QGraphicsView 概率弧线)、`theme.py`(全部颜色唯一来源)、`i18n.py`(zh/en 集中字典)、`ui_components.py`、`icon_provider.py`
- **无数据库**(JSON 数据文件)、无正式日志体系(logging 仅 data_loader.py 一处)
- 质量闸门:ruff + mypy + pytest(`test.yml` CI);`src/docs/开发文档.md` 是权威开发手册兼 changelog

## 要创建/更新的文件

| 文件 | 动作 |
|---|---|
| `.trellis/spec/model/index.md` | 新建(导航 + Pre-Development Checklist + Quality Check) |
| `.trellis/spec/model/engine.md` | 新建(概率引擎约定:线程安全/缓存契约、计算模式、概率显示格式) |
| `.trellis/spec/model/data.md` | 新建(data_loader 只读契约、双语访问、settings 持久化、app_paths 路径规则) |
| `.trellis/spec/model/error-handling.md` | 新建(数据校验、加载失败处理、异常边界) |
| `.trellis/spec/model/quality.md` | 新建(rules 命令、mypy 零错误、单字母变量禁忌、长文件编辑预防) |
| `.trellis/spec/view/index.md` | 新建(导航 + 检查清单) |
| `.trellis/spec/view/theme.md` | 新建(theme.py 单一颜色来源、build_qss、objectName 契约、retheme) |
| `.trellis/spec/view/i18n.md` | 新建(i18n.py 集中字典、retranslate、perk_i18n.json、语言切换) |
| `.trellis/spec/view/widgets.md` | 新建(QGraphicsView 弧线、ColumnHeaderOverlay、Qt 已知坑) |
| `.trellis/spec/view/app-structure.md` | 新建(主窗口导航、tab 结构、VERSION 读取、快捷键) |
| `.trellis/spec/guides/code-reuse-thinking-guide.md` | 更新(填充项目实例) |
| `.trellis/spec/guides/cross-layer-thinking-guide.md` | 更新(填充项目实例) |
| `.trellis/spec/guides/index.md` | 更新(索引与文件集一致) |
| `.trellis/spec/backend/`(整个目录) | 删除 |

## 规则

- 每一条规范都要指向真实文件/测试/文档证据,禁止通用套话
- 模板结构只是起点:删除、改名、拆分、新增都按仓库实际来
- 不写平台特定指令(除非项目已标准化该平台)
- `.trellis/spec/` 中不得残留占位文本、空标题、模板样板

## 验收标准

- [ ] spec 结构变为 `model/` + `view/` + `guides/`,`backend/` 已删除
- [ ] 每个 spec 文件包含真实代码示例、文件路径、反模式,无占位文本
- [ ] 各 `index.md` 与最终文件集一致
- [ ] `grep -R "To be filled\|TODO: fill\|placeholder" .trellis/spec` 无结果
- [ ] 产品源码、测试、CLAUDE.md、docs 零改动(git status 无意外变更)
- [ ] ruff + pytest 仍通过(规范不破坏 CI)

# 视图层开发规范(UI)

> 适用范围:`src/` 中依赖 Qt 的模块 —— `main_window.py`、`tab_forward.py`、`tab_reverse.py`、`tab_builds.py`、`tab_about.py`、`skill_tree_widget.py`、`ui_components.py`、`theme.py`、`i18n.py`、`icon_provider.py`。模型层规范见 [`../model/index.md`](../model/index.md)。

## 文件索引

| 指南 | 内容 |
|------|------|
| [theme.md](./theme.md) | 颜色单一来源、QSS 生成、objectName 契约、retheme |
| [i18n.md](./i18n.md) | 集中双语字典、retranslate、语言切换联动 |
| [widgets.md](./widgets.md) | skill_tree_widget 概率弧线、ColumnHeaderOverlay、Qt 已知坑 |
| [app-structure.md](./app-structure.md) | 主窗口导航、四 tab 职责、VERSION、快捷键 |

## Pre-Development Checklist(改 UI 前)

- [ ] 新增颜色已进 `theme.py` 的 LIGHT/DARK token,未写颜色字面量
- [ ] 新增控件用 `setObjectName` + `build_qss()` 选择器,未用内联 `setStyleSheet`
- [ ] 新增用户可见字符串已加 `i18n._add()` 词条并用 `t()` 取,未硬编码
- [ ] 涉及语言/主题切换的代码记得挂进 `retranslate()` / `retheme()`
- [ ] 新容器组件验证过暗色主题(见 [theme.md](./theme.md) 的 QScrollArea 坑)

## Quality Check(UI 改动后)

- [ ] `ruff check src tests` + `python -m mypy src` 干净
- [ ] `python -m pytest tests/test_ui_smoke.py -q` 通过
- [ ] 两种语言(zh/en)+ 两种主题(light/dark)各切换一次,无残留英文/色块错乱
- [ ] 概率显示仍为 `f"{p*100:.1f}%"` 格式(见 [../model/quality.md](../model/quality.md))
- [ ] 长文件(tab 各 ~600-800 行、`skill_tree_widget.py` 825 行)编辑后确认尾部完整

# 自定义控件规范(skill_tree_widget / ui_components)

适用时机:修改 `src/skill_tree_widget.py`(概率矩阵视图)、`src/ui_components.py`(通用组件),或新增自绘控件。

## SkillTreeView 概率矩阵

`SkillTreeView(QGraphicsView)`(`skill_tree_widget.py:433`)呈现 7 层 × N 组 perk 矩阵,概率弧线是其标志性视觉:

- 节点:`SkillNode(QGraphicsEllipseItem)`(`:169`),`paint()`(`:207`)自绘
- 概率 → 颜色映射:`prob_fill_color(p)`(`:154`)、`prob_halo_color(p)`(`:159`)、`prob_border_color(p)`(`:165`)—— 这些函数里的颜色必须走 `theme.py` token(见 [theme.md](./theme.md))
- 数据组装:`build_skill_tree_data(gd, results)`(`:46`)、`_compute_composition()`(`:74`);tier 标签 `_tier_labels()`(`:148`)为双语
- 弧线/填充概率颜色等代码内颜色需在 `retheme()`(`:635`)重绘

## ColumnHeaderOverlay(不要移回 drawForeground)

列头由 `ColumnHeaderOverlay(QWidget)`(`skill_tree_widget.py:326`)子控件绘制,**不是** `SkillTreeView.drawForeground()`:

- 原因(Qt6):`drawForeground` 的 exposed-rect 裁剪坐标不可靠,源码注释明确说明 `:330-331` —— 用标准 widget `paintEvent` 规避
- 新增列头交互(悬停、点击)应加在 `ColumnHeaderOverlay` 的事件方法(`mouseMoveEvent` `:353`、`paintEvent` `:363`)里
- **反模式**:把列头绘制逻辑移回 view 的 `drawForeground` —— 裁剪问题会重现,且这是项目历史踩过的坑

## 通用组件(ui_components.py)

`src/ui_components.py` 已有可复用件,新增占位/提示 UI 前先查:

- `make_placeholder(text, sub_text=..., icon_provider=...)`(`:12`)、`make_notice_parchment(title, body)`(`:49`)、`make_error_notice(title, body)`(`:70`)
- `CollapsibleSection(QWidget)`(`:90`)折叠区块
- 提示文案必须走 `t()`(见 [i18n.md](./i18n.md))

## 图标

- 图标资源统一经 `src/icon_provider.py`(345 行)提供;资源缺失时应降级(占位符),不崩溃 —— 资源错误抛 `IconError`(见 [../model/error-handling.md](../model/error-handling.md))

## Qt 已知坑(新增控件时)

- QCompleter 需显式 `QStringListModel`;QScrollArea 视口暗色回退;QSS 子控件规则覆盖 ID 选择器 —— 详见 [theme.md](./theme.md)
- `QGraphicsView` 场景缩放/滚轮事件改动后需手动验证 tooltip(`SkillNode.hoverMoveEvent` `:291` 与 `_show_tooltip` `:297`)与列头坐标仍对齐

## 参考

- `tests/test_ui_smoke.py`;根 `CLAUDE.md` View layer 节

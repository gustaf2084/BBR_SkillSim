# 主题与样式规范(theme.py)

适用时机:任何涉及颜色的改动,或新增需要样式化的控件。

## 单一颜色来源(强制)

`src/theme.py` 是**唯一**的颜色权威:

- `LIGHT`(`theme.py:17`)与 `DARK`(`theme.py:91`)两个 token dict,键名语义化(`window_bg`、`surface`、`accent`、`accent_hover`、`text_muted`、`nav_selected`、`parchment_bg`、`error_bg` 等)
- 取色通过 `theme.c(key)`(`theme.py:192`,与 `set_theme`/`theme_name`/`is_dark` 配套)
- **反模式**:在任何 .py 或 QSS 里写颜色字面量(如 `#B8860B`)—— 换主题时该处不会变,成为"鬼颜色"。需要新颜色先加 token,再引用

## QSS 生成与覆盖

- `build_qss()`(`theme.py:238`)运行时生成整份样式表,仓库内无 .qss 文件
- 用户覆盖层:`main.py:54` 把 exe 相邻的 `style.qss`(用户自写)追加在 `build_qss()` 之后 —— 仅用户自定义时存在,仓库不提供
- 样式控件的方式是 `setObjectName()` + `build_qss()` 里的 ID 选择器,不用内联 `setStyleSheet()`;objectName 契约表见 `src/docs/开发文档.md` §5.2

## 代码内颜色与 retheme(易漏)

QSS 之外的取色路径(不随样式表刷新),必须在 `retheme()` 里重绘:

- QPainter 绘制(QGraphicsView 场景、弧线)
- 表格/列表项颜色、富文本 HTML 里的颜色
- 各 tab 的 `retheme()` 签名一致:`tab_forward.py:428`、`tab_reverse.py:299`、`tab_builds.py:277`、`tab_about.py:97`、`skill_tree_widget.py:635`
- 新增任何代码内颜色时必须扩展对应 `retheme()`,否则切主题后该颜色残留旧值

## 已知 Qt 坑(改容器/样式前必读)

- **QSS 子控件规则覆盖 ID 选择器**:`QListWidget::item { color }` 之类会压过 `#objName { color }`,两者冲突时以子控件规则为准
- **QScrollArea viewport 暗色失效**:滚动区域视口在暗色主题下会回退到系统(浅色)调色板 —— 新容器组件必须做暗色检查,必要时显式给 viewport 设背景
- **QCompleter 需要显式 QStringListModel**:直接塞 list 不生效,必须 `QCompleter(QStringListModel(...))`

## 参考

- 行为契约:根 `CLAUDE.md` Cross-cutting conventions 节;`tests/test_ui_smoke.py`

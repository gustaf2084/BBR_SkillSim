# -*- coding: utf-8 -*-
"""theme.py — 设计令牌单一数据源(浅色/深色)+ 全局 QSS 生成。

所有 UI 颜色都从这里取值;禁止在其他模块写颜色字面量。
纯 Python 模块(不依赖 Qt),可被 i18n 等底层模块安全导入。

Usage:
    import theme
    theme.set_theme("dark")
    app.setStyleSheet(theme.build_qss())
    color_hex = theme.c("accent")
    tier_hex = theme.prob_color(0.85)
"""

# ── 调色板令牌 ──────────────────────────────────────────────────

LIGHT = {
    # 基础表面
    "window_bg":      "#F5F0E8",
    "surface":        "#FFFFFF",
    "sunken":         "#F0EDE6",
    "hover":          "#EBE4D6",
    "pressed":        "#DDD4C2",
    "row_alt":        "#FAF7F0",
    # 边框
    "border":         "#DDD6CC",
    "border_strong":  "#C8BFA8",
    # 文字
    "text":           "#1C1814",
    "text_muted":     "#6B6359",
    "text_faint":     "#A09888",
    # 强调色(金)
    "accent":         "#B8860B",
    "accent_hover":   "#C7950C",
    "accent_pressed": "#9A6F09",
    "accent_soft":    "#F0E8D4",
    "accent_deep":    "#8B6914",
    "on_accent":      "#FFFFFF",
    # 输入控件
    "input_bg":       "#FFFFFF",
    "input_bg_alt":   "#FFFEF9",
    # 导航栏
    "nav_bg":         "#2C2416",
    "nav_border":     "#1A1510",
    "nav_hover":      "#3A3024",
    "nav_selected":   "#4A3D26",
    "nav_text":       "#C8BFA8",
    "nav_text_hover": "#E0D8C0",
    "nav_text_faint": "#9B9285",
    "nav_divider":    "#3A3024",
    # 羊皮纸提示 / 错误提示
    "parchment_bg":     "#FDF8F0",
    "parchment_border": "#C8BFA8",
    "parchment_title":  "#8B6914",
    "error_bg":       "#FDF0F0",
    "error_border":   "#C0392B",
    "error_title":    "#8B1A1A",
    "error_text":     "#5A1A1A",
    "danger":         "#8B1A1A",
    "danger_hover":   "#A01E1E",
    "danger_soft_bg": "#F5E3E0",
    # 工具提示(两套主题统一:深棕底金边)
    "tooltip_bg":     "#2C2416",
    "tooltip_text":   "#E0D8C0",
    # 表格
    "table_grid":     "#EBE4D6",
    # 技能树矩阵
    "matrix_bg":            "#FAFAF6",
    "matrix_header_bg":     "#F2F0E8",
    "matrix_corner":        "#E8E4D8",
    "matrix_grid":          "#E0DCD0",
    "matrix_header_border": "#D0CCC0",
    "matrix_row_text":      "#6B6359",
    "matrix_header_text":   "#333333",
    # 纯度列底色
    "purity_good_bg": "#E4EFE7",
    "purity_bad_bg":  "#F5E6E1",
    # 滚动条
    "scroll_handle":       "#C8BFA8",
    "scroll_handle_hover": "#B0A890",
    # 概率条轨道
    "bar_track":      "#F0EDE6",
    "bar_border":     "#DDD6CC",
}

DARK = {
    "window_bg":      "#1E1912",
    "surface":        "#262019",
    "sunken":         "#1A1510",
    "hover":          "#332B1F",
    "pressed":        "#3D3323",
    "row_alt":        "#221C14",
    "border":         "#3A3226",
    "border_strong":  "#55492F",
    "text":           "#E4DCC8",
    "text_muted":     "#A89F8C",
    "text_faint":     "#6E6656",
    "accent":         "#C99620",
    "accent_hover":   "#D9A82E",
    "accent_pressed": "#A87D14",
    "accent_soft":    "#3D3420",
    "accent_deep":    "#D9A82E",
    "on_accent":      "#1C1408",
    "input_bg":       "#211B13",
    "input_bg_alt":   "#241E15",
    "nav_bg":         "#14100A",
    "nav_border":     "#0A0806",
    "nav_hover":      "#262019",
    "nav_selected":   "#33291A",
    "nav_text":       "#C8BFA8",
    "nav_text_hover": "#E8DFC8",
    "nav_text_faint": "#857C68",
    "nav_divider":    "#2C2416",
    "parchment_bg":     "#2B2418",
    "parchment_border": "#55492F",
    "parchment_title":  "#D9A82E",
    "error_bg":       "#2E1B18",
    "error_border":   "#B0453A",
    "error_title":    "#E07B6E",
    "error_text":     "#D9A99F",
    "danger":         "#B0453A",
    "danger_hover":   "#C2564A",
    "danger_soft_bg": "#3A2320",
    "tooltip_bg":     "#2C2416",
    "tooltip_text":   "#E0D8C0",
    "table_grid":     "#332B1F",
    "matrix_bg":            "#201A12",
    "matrix_header_bg":     "#262019",
    "matrix_corner":        "#2C2517",
    "matrix_grid":          "#332B1F",
    "matrix_header_border": "#3A3226",
    "matrix_row_text":      "#A89F8C",
    "matrix_header_text":   "#D8D0BC",
    "purity_good_bg": "#263223",
    "purity_bad_bg":  "#3A2320",
    "scroll_handle":       "#55492F",
    "scroll_handle_hover": "#6B5C3D",
    "bar_track":      "#2C2517",
    "bar_border":     "#3A3226",
}

# ── 概率分层色(高→无,5 档)──────────────────────────────────
# 阈值:>=0.80 / >=0.50 / >=0.20 / >0 / =0

_PROB_LIGHT = ["#27704B", "#A0522D", "#5A6B7D", "#8B8378", "#B0B0B0"]
_PROB_DARK = ["#4CAF7D", "#C97B4A", "#8FA3B8", "#A39B8B", "#6B6B6B"]

# ── 类别徽章底色(白字,两套主题共用)────────────────────────
CAT_COLOR = {
    "Shared":         "#27704B",
    "Exclusive":      "#8B6914",
    "Weapon":         "#5A6B7D",
    "Armor":          "#7B6B5A",
    "Fighting Style": "#8B1A6B",
    "Special":        "#B8860B",
    "Always":         "#4A4A4A",
}

CAT_ORDER = ["Shared", "Exclusive", "Weapon", "Armor", "Fighting Style", "Special"]

# ── 主题状态 ────────────────────────────────────────────────────

_current_name = "light"
_current = LIGHT


def set_theme(name):
    """切换当前主题。'light' 或 'dark'。"""
    global _current_name, _current
    _current_name = "dark" if name == "dark" else "light"
    _current = DARK if _current_name == "dark" else LIGHT


def theme_name():
    return _current_name


def is_dark():
    return _current_name == "dark"


def c(key):
    """取当前主题的令牌颜色(hex 字符串)。"""
    return _current[key]


def _prob_index(p):
    if p >= 0.80:
        return 0
    if p >= 0.50:
        return 1
    if p >= 0.20:
        return 2
    if p > 0:
        return 3
    return 4


def prob_color(p):
    """概率 → 分层色(hex),随主题自动调整明度。"""
    palette = _PROB_DARK if is_dark() else _PROB_LIGHT
    return palette[_prob_index(p)]


def prob_palette():
    """当前主题的 5 档概率色列表(高→无)。"""
    return list(_PROB_DARK if is_dark() else _PROB_LIGHT)


def _lighten(hex_color, factor):
    """按比例向白色靠拢(factor 0~1)。纯 Python,不依赖 Qt。"""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02X}{g:02X}{b:02X}"


def cat_text_color(cat):
    """类别标题文字色:浅色主题用原色,深色主题提亮保证对比度。"""
    base = CAT_COLOR.get(cat, c("text_muted"))
    return _lighten(base, 0.35) if is_dark() else base


# ── 全局 QSS 生成 ───────────────────────────────────────────────

def build_qss():
    """从当前主题令牌生成全局样式表。"""
    return f"""
/* ── 全局默认 ── */
QWidget {{
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
    color: {c("text")};
}}

QMainWindow, QStackedWidget, QDialog {{
    background-color: {c("window_bg")};
}}

/* ── 导航栏 ── */
#nav_panel {{
    background-color: {c("nav_bg")};
    border-right: 1px solid {c("nav_border")};
}}

#nav_title {{
    background: transparent;
    color: {c("nav_text_hover")};
    border-left: 3px solid {c("accent")};
    padding-left: 11px;
}}

#nav_list {{
    background: {c("nav_bg")};
    border: none;
    color: {c("nav_text")};
    font-size: 14px;
    font-weight: bold;
    outline: none;
}}

#nav_list::item {{
    padding: 10px 14px;
    border-left: 3px solid transparent;
    border-bottom: none;
    color: {c("nav_text")};
}}

#nav_list::item:hover {{
    background: {c("nav_hover")};
    color: {c("nav_text_hover")};
}}

#nav_list::item:selected {{
    background: {c("nav_selected")};
    color: {c("nav_text_hover")};
    border-left: 3px solid {c("accent")};
}}

#nav_version {{
    color: {c("nav_text_faint")};
    font-size: 11px;
    padding: 6px 14px 8px 14px;
    background: transparent;
    border-top: 1px solid {c("nav_divider")};
}}

#nav_foot_btn {{
    font-size: 11px;
    color: {c("nav_text_faint")};
    background: transparent;
    border: 1px solid {c("nav_divider")};
    border-radius: 4px;
    padding: 2px 8px;
    margin: 2px 14px;
    min-width: 72px;
    min-height: 18px;
}}

#nav_foot_btn:hover {{
    color: {c("nav_text")};
    border-color: {c("accent")};
}}

/* ── 按钮 ── */
QPushButton {{
    background-color: {c("window_bg")};
    color: {c("text")};
    border: 1px solid {c("border_strong")};
    border-radius: 4px;
    padding: 6px 14px;
    min-height: 22px;
}}

QPushButton:hover {{
    background-color: {c("hover")};
    border-color: {c("accent")};
}}

QPushButton:pressed {{
    background-color: {c("pressed")};
}}

QPushButton:disabled {{
    background-color: {c("sunken")};
    color: {c("text_faint")};
    border-color: {c("border")};
}}

QPushButton#primary_btn {{
    background-color: {c("accent")};
    color: {c("on_accent")};
    border: 1px solid {c("accent_pressed")};
    font-size: 14px;
    font-weight: bold;
    padding: 10px 20px;
}}

QPushButton#primary_btn:hover {{ background-color: {c("accent_hover")}; }}
QPushButton#primary_btn:pressed {{ background-color: {c("accent_pressed")}; }}
QPushButton#primary_btn:disabled {{
    background-color: {c("border_strong")};
    color: {c("surface")};
    border-color: {c("border")};
}}

QPushButton#danger_btn {{
    background-color: {c("danger")};
    color: #FFFFFF;
    border: 1px solid {c("danger_hover")};
}}

QPushButton#danger_btn:hover {{ background-color: {c("danger_hover")}; }}

/* 次要按钮(复制/导出等) */
QPushButton#secondary_btn {{
    background: transparent;
    padding: 4px 16px;
    border: 1px solid {c("border_strong")};
    border-radius: 4px;
    font-size: 12px;
}}

QPushButton#secondary_btn:hover {{
    background: {c("hover")};
    border-color: {c("accent")};
}}

/* 取消按钮(浅危险色) */
QPushButton#cancel_btn {{
    font-size: 11px;
    padding: 4px 12px;
    background: {c("danger_soft_bg")};
    border: 1px solid {c("error_border")};
    border-radius: 4px;
    color: {c("error_title")};
}}

QPushButton#cancel_btn:hover {{
    background: {c("error_bg")};
}}

/* 虚线圆角按钮(+ 新建流派 / + 添加组) */
QPushButton#dashed_btn {{
    font-size: 11px;
    padding: 2px 10px;
    background: transparent;
    color: {c("text_muted")};
    border: 1px dashed {c("border_strong")};
    border-radius: 12px;
}}

QPushButton#dashed_btn:hover {{
    border-color: {c("accent")};
    color: {c("accent")};
}}

/* 小工具按钮(编辑 / 打开文件夹) */
QPushButton#tool_btn {{
    font-size: 11px;
    padding: 2px 8px;
    background: transparent;
    color: {c("text_muted")};
    border: 1px solid {c("border")};
    border-radius: 4px;
}}

QPushButton#tool_btn:hover {{
    border-color: {c("border_strong")};
    color: {c("text")};
}}

/* 可勾选标签按钮(流派 tag) */
QPushButton#chip_btn {{
    font-size: 11px;
    padding: 3px 10px;
    background: {c("window_bg")};
    color: {c("text")};
    border: 1px solid {c("border")};
    border-radius: 12px;
}}

QPushButton#chip_btn:hover {{ border-color: {c("border_strong")}; }}

QPushButton#chip_btn:checked {{
    background: {c("accent")};
    color: {c("on_accent")};
    border-color: {c("accent_pressed")};
}}

/* ── 折叠面板 ── */
QToolButton#collapse_header {{
    background: {c("sunken")};
    color: {c("text")};
    border: 1px solid {c("border")};
    border-radius: 4px;
    padding: 6px 8px;
    font-size: 13px;
    font-weight: 600;
    text-align: left;
}}

QToolButton#collapse_header:hover {{
    background: {c("hover")};
    border-color: {c("border_strong")};
}}

QToolButton#collapse_header:checked {{
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
}}

#collapse_body {{
    background: {c("surface")};
    border: 1px solid {c("border")};
    border-top: none;
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 4px;
}}

/* ── 输入控件 ── */
QComboBox {{
    background-color: {c("input_bg")};
    border: 1px solid {c("border_strong")};
    border-radius: 4px;
    padding: 5px 8px;
    min-height: 22px;
    color: {c("text")};
}}

QComboBox:hover, QComboBox:focus {{ border-color: {c("accent")}; }}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 20px;
    border-left: 1px solid {c("border")};
}}

QComboBox QAbstractItemView {{
    background-color: {c("input_bg")};
    border: 1px solid {c("border_strong")};
    selection-background-color: {c("hover")};
    selection-color: {c("text")};
    outline: none;
}}

QLineEdit {{
    background-color: {c("input_bg")};
    border: 1px solid {c("border_strong")};
    border-radius: 4px;
    padding: 5px 8px;
    color: {c("text")};
}}

QLineEdit:focus {{ border-color: {c("accent")}; }}

QLineEdit#search_input {{
    padding: 4px 8px;
    border: 1px solid {c("border")};
    background: {c("input_bg_alt")};
    font-size: 12px;
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {c("input_bg")};
    border: 1px solid {c("border_strong")};
    border-radius: 4px;
    padding: 4px 6px;
    min-height: 22px;
    color: {c("text")};
}}

QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {c("accent")}; }}

/* ── 复选框 ── */
QCheckBox {{
    spacing: 8px;
    color: {c("text")};
}}

QCheckBox:disabled {{ color: {c("text_faint")}; }}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {c("border_strong")};
    border-radius: 3px;
    background-color: {c("input_bg")};
}}

QCheckBox::indicator:hover {{ border-color: {c("accent")}; }}

QCheckBox::indicator:checked {{
    background-color: {c("accent")};
    border-color: {c("accent_pressed")};
}}

QCheckBox::indicator:disabled {{
    border-color: {c("border")};
    background-color: {c("sunken")};
}}

QCheckBox#trait_badge {{
    spacing: 4px;
    padding: 2px 6px;
    font-size: 11px;
    background: transparent;
    border: 1px solid {c("border")};
    border-radius: 4px;
}}

QCheckBox#trait_badge:hover {{
    background-color: {c("window_bg")};
    border-color: {c("border_strong")};
}}

QCheckBox#trait_badge:checked {{
    background-color: {c("accent_soft")};
    border-color: {c("accent")};
    color: {c("accent_deep")};
}}

/* ── 分组框 ── */
QGroupBox {{
    font-size: 15px;
    font-weight: 600;
    color: {c("text")};
    border: 1px solid {c("border")};
    border-radius: 6px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    background-color: {c("surface")};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 10px;
    margin-left: 12px;
}}

/* ── 表格 ── */
QTableWidget {{
    background-color: {c("surface")};
    alternate-background-color: {c("row_alt")};
    border: 1px solid {c("border")};
    border-radius: 4px;
    gridline-color: {c("table_grid")};
    selection-background-color: {c("accent_soft")};
    selection-color: {c("text")};
    outline: none;
}}

QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {c("sunken")};
}}

QTableWidget::item:selected {{ background-color: {c("accent_soft")}; }}

QHeaderView::section {{
    background-color: {c("window_bg")};
    color: {c("text")};
    font-weight: bold;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid {c("border_strong")};
    border-right: 1px solid {c("border")};
}}

QHeaderView::section:last {{ border-right: none; }}

/* ── 列表控件 ── */
QListWidget {{
    background-color: {c("surface")};
    border: 1px solid {c("border")};
    border-radius: 4px;
    outline: none;
}}

QListWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {c("sunken")};
    color: {c("text")};
}}

QListWidget::item:selected {{
    background-color: {c("accent_soft")};
    color: {c("text")};
}}

QListWidget::item:hover {{ background-color: {c("window_bg")}; }}

/* ── 进度条 ── */
QProgressBar {{
    background-color: {c("bar_track")};
    border: 1px solid {c("bar_border")};
    border-radius: 3px;
    text-align: center;
    color: {c("text")};
    min-height: 14px;
    max-height: 18px;
}}

QProgressBar::chunk {{
    background-color: {c("accent")};
    border-radius: 2px;
}}

/* ── 滚动区域 ──
   QScrollArea 视口默认用系统调色板(白色)填充,深色主题下会露出白底;
   统一改为透明,显示父级窗口背景 */
QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

/* ── 滚动条 ── */
QScrollBar:horizontal {{
    background-color: {c("window_bg")};
    height: 10px;
    border: none;
}}

QScrollBar::handle:horizontal {{
    background-color: {c("scroll_handle")};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{ background-color: {c("scroll_handle_hover")}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

QScrollBar:vertical {{
    background-color: {c("window_bg")};
    width: 10px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background-color: {c("scroll_handle")};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{ background-color: {c("scroll_handle_hover")}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── 分割器 ── */
QSplitter::handle {{
    background-color: {c("border")};
    width: 2px;
    height: 2px;
}}

QSplitter::handle:hover {{ background-color: {c("accent")}; }}

/* ── 工具提示(深棕底金边,两套主题统一)── */
QToolTip {{
    background-color: {c("tooltip_bg")};
    color: {c("tooltip_text")};
    border: 1px solid {c("accent")};
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 12px;
}}

/* ── 状态栏 ── */
QStatusBar {{
    background-color: {c("window_bg")};
    color: {c("text_muted")};
    border-top: 1px solid {c("border")};
    font-size: 12px;
    padding: 2px 10px;
}}

QStatusBar QLabel {{
    color: {c("text_muted")};
    font-size: 11px;
}}

/* ── 消息框 / 菜单 ── */
QMessageBox {{ background-color: {c("surface")}; }}

QMenu {{
    background-color: {c("surface")};
    color: {c("text")};
    border: 1px solid {c("border_strong")};
}}

QMenu::item {{ padding: 5px 24px 5px 12px; }}

QMenu::item:selected {{
    background-color: {c("accent_soft")};
    color: {c("text")};
}}

/* ── 页面标题 ── */
#page_title {{
    font-size: 20px;
    font-weight: bold;
    color: {c("text")};
    padding: 6px 0;
    letter-spacing: 1px;
}}

#section_title {{
    font-size: 15px;
    font-weight: 600;
    color: {c("text")};
    padding: 4px 0;
}}

/* ── 表格说明文字 / 弱提示 ── */
#caption_label {{
    font-size: 12px;
    color: {c("text_muted")};
    padding: 2px 6px;
}}

#summary_label {{
    font-size: 13px;
    color: {c("text_muted")};
    padding: 4px;
}}

/* ── 信息卡片 ── */
#card {{
    background-color: {c("surface")};
    border: 1px solid {c("border")};
    border-radius: 6px;
    padding: 14px;
}}

#card:hover {{ border-color: {c("border_strong")}; }}

#card_body {{
    font-size: 12px;
    color: {c("text")};
}}

/* ── 便签风格提示(空/错误状态)── */
#notice_parchment {{
    background-color: {c("parchment_bg")};
    border: 2px solid {c("parchment_border")};
    border-radius: 8px;
    padding: 20px 24px;
    color: {c("text")};
    font-size: 14px;
}}

#notice_parchment_title {{
    font-size: 16px;
    font-weight: bold;
    color: {c("parchment_title")};
}}

#notice_parchment_body {{
    font-size: 14px;
    color: {c("text")};
    padding-top: 4px;
}}

#notice_error {{
    background-color: {c("error_bg")};
    border: 2px solid {c("error_border")};
    border-radius: 8px;
    padding: 16px 20px;
    color: {c("error_title")};
    font-size: 14px;
}}

/* ── 引导 / 说明盒 ── */
#hint_box {{
    font-size: 12px;
    color: {c("text_muted")};
    padding: 6px 12px;
    background: {c("window_bg")};
    border-radius: 4px;
}}

#playstyle_box {{
    font-size: 12px;
    color: {c("text")};
    padding: 8px;
    background: {c("row_alt")};
    border-radius: 4px;
}}

#playstyle_box[error="true"] {{
    font-size: 11px;
    color: {c("error_title")};
    background: {c("error_bg")};
}}

#traits_hint {{
    font-size: 12px;
    color: {c("accent_deep")};
    background: {c("parchment_bg")};
    padding: 4px 10px;
    border-radius: 4px;
    font-weight: bold;
}}

/* ── 空状态占位 ── */
#placeholder_icon {{
    font-size: 28px;
    color: {c("border_strong")};
}}

#placeholder_text {{
    font-size: 15px;
    color: {c("text_muted")};
    padding: 10px;
}}

#placeholder_sub {{
    font-size: 12px;
    color: {c("text_faint")};
}}

/* ── v0.3.0: 属性范围面板 ── */
#attrPanel {{
    background-color: {c("parchment_bg")};
    border: 1px solid {c("border")};
    border-radius: 4px;
    padding: 8px;
}}

#attrLabel {{
    font-size: 12px;
    font-weight: bold;
    color: {c("text")};
    min-width: 70px;
}}

#attrValues {{
    font-size: 11px;
    color: {c("text_muted")};
    font-family: "Consolas", monospace;
    min-width: 60px;
}}

#attrEstimateLabel {{
    font-size: 10px;
    color: {c("error_border")};
    font-style: italic;
}}

/* ── v0.3.0: 天赋星级控件 ── */
#starLabel {{
    font-size: 12px;
    color: {c("text")};
    min-width: 70px;
}}

#starCombo {{
    font-size: 12px;
    min-width: 60px;
    padding: 2px 6px;
}}

/* ── 技能树 chip 栏 ── */
#st_chip {{
    background: {c("window_bg")};
    border: 1px solid {c("border")};
    border-radius: 12px;
    padding: 2px;
}}

#st_chip:hover {{ border-color: {c("border_strong")}; }}

#st_chip_label {{
    font-size: 11px;
    color: {c("text")};
    background: transparent;
    border: none;
}}

#st_chip_close {{
    font-size: 12px;
    border: none;
    background: transparent;
    color: {c("text_faint")};
    border-radius: 9px;
    padding: 0;
    min-height: 16px;
}}

#st_chip_close:hover {{
    background: {c("danger_soft_bg")};
    color: {c("error_border")};
}}

#st_legend {{
    font-size: 11px;
    color: {c("text_faint")};
    padding: 0 6px;
}}
"""

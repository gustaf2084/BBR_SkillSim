# -*- coding: utf-8 -*-
"""
ui_components.py
统一的可复用 UI 组件：空状态、错误状态、引导提示、折叠面板。
所有颜色通过 objectName 由全局 QSS(theme.build_qss)控制。
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QSizePolicy, QToolButton, QVBoxLayout, QWidget


def make_placeholder(text, sub_text=""):
    """创建就绪/等待状态提示组件。"""
    w = QWidget()
    v = QVBoxLayout(w)
    v.setAlignment(Qt.AlignCenter)
    v.setContentsMargins(20, 40, 20, 40)

    icon = QLabel("◈")
    icon.setObjectName("placeholder_icon")
    icon.setAlignment(Qt.AlignCenter)
    v.addWidget(icon)

    label = QLabel(text)
    label.setObjectName("placeholder_text")
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignCenter)
    v.addWidget(label)

    sub = QLabel(sub_text)
    sub.setObjectName("placeholder_sub")
    sub.setWordWrap(True)
    sub.setAlignment(Qt.AlignCenter)
    sub.setVisible(bool(sub_text))
    v.addWidget(sub)

    # 暴露给调用方以便 retranslate
    w.title_label = label
    w.sub_label = sub
    return w


def make_notice_parchment(title, body):
    """创建羊皮纸便签风格提示（无结果/空状态）。"""
    w = QWidget()
    w.setObjectName("notice_parchment")
    v = QVBoxLayout(w)

    t = QLabel(title)
    t.setObjectName("notice_parchment_title")
    t.setWordWrap(True)
    v.addWidget(t)

    b = QLabel(body)
    b.setObjectName("notice_parchment_body")
    b.setWordWrap(True)
    v.addWidget(b)

    w.title_label = t
    w.body_label = b
    return w


def make_error_notice(title, body):
    """创建错误提示组件。"""
    w = QWidget()
    w.setObjectName("notice_error")
    v = QVBoxLayout(w)

    t = QLabel(title)
    t.setStyleSheet("font-size: 16px; font-weight: bold;")
    t.setWordWrap(True)
    v.addWidget(t)

    b = QLabel(body)
    b.setWordWrap(True)
    v.addWidget(b)

    w.title_label = t
    w.body_label = b
    return w


class CollapsibleSection(QWidget):
    """真折叠面板：标题按钮(带箭头) + 可显隐内容区。

    替代 checkable QGroupBox(后者取消勾选只禁用子控件、不收起内容)。

    Usage:
        sec = CollapsibleSection("高级选项", expanded=False)
        form = QFormLayout(sec.content)
        form.addRow(...)
        layout.addWidget(sec)
    """

    toggled = Signal(bool)

    def __init__(self, title="", expanded=False, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        self.header = QToolButton()
        self.header.setObjectName("collapse_header")
        self.header.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.header.setCheckable(True)
        self.header.setChecked(expanded)
        self.header.setCursor(Qt.PointingHandCursor)
        self.header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.header.setMinimumHeight(30)
        self.header.clicked.connect(self._on_toggle)
        v.addWidget(self.header)

        self.content = QWidget()
        self.content.setObjectName("collapse_body")
        self.content.setVisible(expanded)
        v.addWidget(self.content)

        self._title = title
        self._apply_header()

    def _apply_header(self):
        arrow = "▾" if self.header.isChecked() else "▸"
        self.header.setText(f"{arrow}  {self._title}")

    def _on_toggle(self, checked):
        self.content.setVisible(checked)
        self._apply_header()
        self.toggled.emit(checked)

    # ── Public API ──

    def set_title(self, title):
        self._title = title
        self._apply_header()

    def title(self):
        return self._title

    def is_expanded(self):
        return self.header.isChecked()

    def set_expanded(self, expanded):
        if self.header.isChecked() != expanded:
            self.header.setChecked(expanded)
            self._on_toggle(expanded)

    def set_title_color(self, color_hex):
        """给标题按钮附加文字颜色(用于类别面板着色)。"""
        self.header.setStyleSheet(f"QToolButton#collapse_header {{ color: {color_hex}; }}")

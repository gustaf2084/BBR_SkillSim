# -*- coding: utf-8 -*-
"""
ui_components.py
统一的可复用 UI 组件：空状态、错误状态、引导提示、折叠面板、
数值排序表格项、概率条委托、流式布局、可删除标签栏。
所有颜色通过 objectName 由全局 QSS(theme.build_qss)控制。
"""

from PySide6.QtCore import QPoint, QRect, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

import theme

# 表格排序用的数值角色(UserRole 已被各表用来存 id / 概率)
SORT_ROLE = Qt.ItemDataRole.UserRole + 1


def make_placeholder(text, sub_text="", icon_provider=None):
    """创建就绪/等待状态提示组件。"""
    w = QWidget()
    v = QVBoxLayout(w)
    v.setAlignment(Qt.AlignCenter)
    v.setContentsMargins(20, 40, 20, 40)

    if icon_provider is not None:
        pix = icon_provider.get_placeholder_pixmap(theme.c("border_strong"), 36)
        icon = QLabel()
        icon.setPixmap(pix)
    else:
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
    t.setObjectName("notice_error_title")
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


class NumericItem(QTableWidgetItem):
    """按 SORT_ROLE 数值排序的表格项(避免 "9.5%" > "10.0%" 的文本排序)。"""

    def __init__(self, text="", sort_value=0.0):
        super().__init__(text)
        self.setData(SORT_ROLE, float(sort_value))

    def __lt__(self, other):
        a = self.data(SORT_ROLE)
        b = other.data(SORT_ROLE)
        if a is None or b is None:
            return super().__lt__(other)
        return float(a) < float(b)


class ProbBarDelegate(QStyledItemDelegate):
    """自绘概率条:扁平圆角实色填充,颜色随概率分层、随主题切换。

    数据约定:index.data(Qt.UserRole) = 概率浮点值(0~1)。
    """

    BAR_HEIGHT = 14
    H_PAD = 8

    def paint(self, painter, option, index):
        # 先画默认背景(选中态/交替行色)
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""
        style = opt.widget.style() if opt.widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, opt.widget)

        p = index.data(Qt.UserRole)
        if p is None:
            return
        p = max(0.0, min(1.0, float(p)))

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        rect = option.rect
        y = rect.y() + (rect.height() - self.BAR_HEIGHT) / 2
        track = QRectF(rect.x() + self.H_PAD, y,
                       rect.width() - self.H_PAD * 2, self.BAR_HEIGHT)
        # 轨道
        painter.setPen(QPen(QColor(theme.c("bar_border")), 1))
        painter.setBrush(QColor(theme.c("bar_track")))
        painter.drawRoundedRect(track, 3, 3)
        # 填充
        fill_w = (track.width() - 2) * p
        if fill_w >= 1:
            fill = QRectF(track.x() + 1, track.y() + 1, fill_w, track.height() - 2)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(theme.prob_color(p)))
            painter.drawRoundedRect(fill, 2, 2)
        painter.restore()


class FlowLayout(QLayout):
    """自动换行的流式布局(Qt 官方 FlowLayout 示例的精简版)。"""

    def __init__(self, parent=None, spacing=4):
        super().__init__(parent)
        self._items = []
        self._spacing = spacing
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), apply=False)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, apply=True)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        return size

    def _do_layout(self, rect, apply):
        x, y = rect.x(), rect.y()
        line_h = 0
        for item in self._items:
            # 用 isHidden 而非 isVisible:新加入、尚未 show 的子控件也要参与布局
            if item.widget() is not None and item.widget().isHidden():
                continue
            hint = item.sizeHint()
            next_x = x + hint.width() + self._spacing
            if next_x - self._spacing > rect.right() and line_h > 0:
                x = rect.x()
                y += line_h + self._spacing
                next_x = x + hint.width() + self._spacing
                line_h = 0
            if apply:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x = next_x
            line_h = max(line_h, hint.height())
        return y + line_h - rect.y()


class ChipBar(QWidget):
    """可删除标签栏:每个标签带 ×,末尾一个"清空"按钮;无标签时自动隐藏。

    Usage:
        bar = ChipBar(clear_text=t("common.clear"))
        bar.removed.connect(on_remove)   # 参数为 key
        bar.cleared.connect(on_clear)
        bar.set_items([(key, text), ...])
    """

    removed = Signal(str)
    cleared = Signal()

    def __init__(self, clear_text="", parent=None):
        super().__init__(parent)
        self.setObjectName("chip_bar")
        self._layout = FlowLayout(self, spacing=4)
        self._clear_text = clear_text
        self._chips = []
        self.setVisible(False)

    def set_clear_text(self, text):
        self._clear_text = text
        for btn in self._chips:
            if btn.property("chip_key") is None:
                btn.setText(text)

    def keys(self):
        return [b.property("chip_key") for b in self._chips
                if b.property("chip_key") is not None]

    def set_items(self, items):
        for btn in self._chips:
            self._layout.removeWidget(btn)
            btn.hide()  # deleteLater 生效前仍会绘制,先隐藏避免残影
            btn.deleteLater()
        self._chips = []
        for key, text in items:
            btn = QToolButton(self)
            btn.setObjectName("target_chip")
            btn.setText(f"{text}  ×")
            btn.setProperty("chip_key", key)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, k=key: self.removed.emit(k))
            self._layout.addWidget(btn)
            self._chips.append(btn)
        if items:
            clear = QPushButton(self._clear_text, self)
            clear.setObjectName("chip_clear")
            clear.setCursor(Qt.PointingHandCursor)
            clear.clicked.connect(self.cleared.emit)
            self._layout.addWidget(clear)
            self._chips.append(clear)
        self.setVisible(bool(items))
        self.updateGeometry()

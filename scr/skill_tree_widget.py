# -*- coding: utf-8 -*-
"""
skill_tree_widget.py
技能树组矩阵可视化组件。
"""

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QBrush, QPen, QFont, QPainter, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsPixmapItem,
    QToolTip, QLabel, QPushButton, QComboBox, QSizePolicy,
)

from perk_zh import get_perk_name_zh, get_perk_desc_zh

# ── 紧凑布局常量 ──────────────────────────────────────────────
NODE_RADIUS = 16
NODE_DIAM = NODE_RADIUS * 2
CELL_W = 74
CELL_H = 38
ROW_HEADER_W = 44
COL_HEADER_H = 36
MATRIX_LEFT = ROW_HEADER_W
MATRIX_TOP = COL_HEADER_H
DEFAULT_MAX_GROUPS = 5

TIER_LABELS = ["1阶", "2阶", "3阶", "4阶", "5阶", "6阶", "7阶"]


def prob_fill_color(p):
    if p >= 0.80:
        return QColor("#27ae60")
    if p >= 0.50:
        return QColor("#52be80")
    if p >= 0.20:
        return QColor("#f4d03f")
    if p > 0:
        return QColor("#e74c3c")
    return QColor("#b0b0b0")


def prob_border_color(p):
    return prob_fill_color(p).darker(130)


class SkillNode(QGraphicsEllipseItem):
    def __init__(self, group_id, tier_label, skill_name, skill_desc, probability, icon_provider=None):
        r = NODE_RADIUS
        super().__init__(-r, -r, NODE_DIAM, NODE_DIAM)
        self.group_id = group_id
        self.tier_label = tier_label
        self.skill_name = skill_name
        self.skill_desc = skill_desc
        self._probability = probability
        self._color = prob_fill_color(probability)
        self._icon_provider = icon_provider
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        self.setBrush(QBrush(self._color))
        self.setPen(QPen(prob_border_color(self._probability), 1.5))
        self.setOpacity(1.0)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self._icon_provider and self.skill_name:
            pix = self._icon_provider.get_perk_icon(self.skill_name, NODE_DIAM)
            if pix and not pix.isNull():
                icon_size = NODE_DIAM - 4
                scaled = pix.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                sx = -scaled.width() // 2
                sy = -scaled.height() // 2
                painter.drawPixmap(int(sx), int(sy), scaled)

    def _tooltip_text(self):
        if not self.skill_name:
            return ""
        zh_name = get_perk_name_zh(self.skill_name)
        zh_desc = get_perk_desc_zh(self.skill_name)
        if not zh_desc and self.skill_desc:
            zh_desc = self.skill_desc.strip()
        lines = [zh_name]
        if zh_desc:
            desc = zh_desc.strip()
            if len(desc) > 240:
                desc = desc[:237] + "..."
            lines.append(chr(0x2500) * 24)
            lines.append(desc)
        lines.append("")
        lines.append("[" + self.group_id + "]  " + self.tier_label)
        return "\n".join(lines)

    def hoverEnterEvent(self, event):
        if self.skill_name:
            self.setPen(QPen(QColor("#ffffff"), 2.5))
            QToolTip.showText(event.screenPos(), self._tooltip_text())
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        QToolTip.hideText()
        self._apply_style()
        super().hoverLeaveEvent(event)

    def hoverMoveEvent(self, event):
        if self.skill_name:
            QToolTip.showText(event.screenPos(), self._tooltip_text())
        super().hoverMoveEvent(event)


class SkillTreeView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setBackgroundBrush(QColor("#fafaf8"))
        self._col_headers = []
        self._h_scroll = 0
        self._hdr_font = QFont("Microsoft YaHei", 9)
        self._hdr_font.setBold(True)
        self._tier_font = QFont("Microsoft YaHei", 9)
        self.horizontalScrollBar().valueChanged.connect(self._on_h_scroll)

    def set_col_headers(self, headers):
        self._col_headers = headers

    def _on_h_scroll(self, value):
        self._h_scroll = value
        self.viewport().update()

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        vp = self.viewport().rect()
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.fillRect(QRectF(0, 0, ROW_HEADER_W, vp.height()), QColor("#f0f0ec"))
        painter.setPen(QPen(QColor("#d0d0c8"), 1))
        painter.drawLine(QPointF(ROW_HEADER_W, 0), QPointF(ROW_HEADER_W, vp.height()))
        painter.setFont(self._tier_font)
        for row in range(7):
            y = MATRIX_TOP + row * CELL_H
            painter.setPen(QColor("#666"))
            painter.drawText(QRectF(0, y, ROW_HEADER_W, CELL_H), Qt.AlignCenter, TIER_LABELS[row])
        painter.fillRect(QRectF(0, 0, vp.width(), COL_HEADER_H), QColor("#f0f0ec"))
        painter.setPen(QPen(QColor("#d0d0c8"), 1))
        painter.drawLine(QPointF(0, COL_HEADER_H - 1), QPointF(vp.width(), COL_HEADER_H - 1))
        if not self._col_headers:
            return
        painter.setFont(self._hdr_font)
        for col, (label, prob) in enumerate(self._col_headers):
            x = MATRIX_LEFT + col * CELL_W - self._h_scroll
            if x + CELL_W < ROW_HEADER_W or x > vp.width():
                continue
            pc = prob_fill_color(prob)
            painter.fillRect(QRectF(x + 4, COL_HEADER_H - 10, 5, 6), pc)
            painter.setPen(QPen(pc.darker(130), 1))
            painter.drawRect(QRectF(x + 4, COL_HEADER_H - 10, 5, 6))
            painter.setPen(QColor("#333"))
            painter.drawText(QRectF(x + 12, 2, CELL_W - 16, COL_HEADER_H - 8),
                           Qt.AlignLeft | Qt.AlignVCenter, label)
        painter.fillRect(QRectF(0, 0, ROW_HEADER_W, COL_HEADER_H), QColor("#e8e8e0"))

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if not self._col_headers:
            return
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.setPen(QPen(QColor("#e0e0d8"), 0.5))
        ncols = len(self._col_headers)
        total_w = MATRIX_LEFT + ncols * CELL_W
        total_h = MATRIX_TOP + 7 * CELL_H
        for col in range(ncols + 1):
            x = MATRIX_LEFT + col * CELL_W
            painter.drawLine(x, MATRIX_TOP, x, total_h)
        for row in range(8):
            y = MATRIX_TOP + row * CELL_H
            painter.drawLine(MATRIX_LEFT, y, total_w, y)


class SkillTreeWidget(QWidget):
    def __init__(self, parent=None, icon_provider=None):
        super().__init__(parent)
        self._icon_provider = icon_provider
        self._all_trees = []
        self._active_ids = set()
        self._scene = QGraphicsScene()
        self._scene.setBackgroundBrush(QColor("#fafaf8"))
        self._view = SkillTreeView(self._scene)
        self._placeholder = QLabel("请选择一个背景并点击计算概率分布")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet("color: #999; font-size: 14px; padding: 30px;")
        self._placeholder.setVisible(True)
        ctrl = QWidget()
        cl = QHBoxLayout(ctrl)
        cl.setContentsMargins(0, 2, 0, 2)
        cl.setSpacing(4)
        cl.addWidget(QLabel("技能组："))
        self._add_combo = QComboBox()
        self._add_combo.setMinimumWidth(150)
        self._add_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cl.addWidget(self._add_combo, 1)
        self._add_btn = QPushButton("添加")
        self._add_btn.clicked.connect(self._on_add)
        cl.addWidget(self._add_btn)
        self._remove_btn = QPushButton("移除")
        self._remove_btn.clicked.connect(self._on_remove)
        cl.addWidget(self._remove_btn)
        self._ctrl_bar = ctrl
        self._ctrl_bar.setVisible(False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._placeholder)
        layout.addWidget(self._ctrl_bar)
        layout.addWidget(self._view, 1)

    def set_trees(self, trees):
        self._all_trees = [t for t in trees if t.get("probability", 0) > 0]
        self._all_trees.sort(key=lambda t: t.get("probability", 0), reverse=True)
        default_n = min(DEFAULT_MAX_GROUPS, len(self._all_trees))
        self._active_ids = {t["group_id"] for t in self._all_trees[:default_n]}
        self._refresh()

    def clear(self):
        self._all_trees = []
        self._active_ids = set()
        self._scene.clear()
        self._view.set_col_headers([])
        self._placeholder.setVisible(True)
        self._ctrl_bar.setVisible(False)
        self._view.setVisible(False)

    def scroll_to_group(self, group_id):
        if group_id not in self._active_ids:
            self._active_ids.add(group_id)
            self._rebuild()
        active = [t for t in self._all_trees if t["group_id"] in self._active_ids]
        for col, t in enumerate(active):
            if t["group_id"] == group_id:
                target_x = MATRIX_LEFT + col * CELL_W - 40
                self._view.horizontalScrollBar().setValue(max(0, target_x))
                return

    def _refresh(self):
        self._update_combo()
        self._rebuild()

    def _update_combo(self):
        self._add_combo.clear()
        for t in self._all_trees:
            pct = int(t.get("probability", 0) * 100)
            is_active = t["group_id"] in self._active_ids
            prefix = "[已显示] " if is_active else ""
            label = prefix + t.get("group_name", t["group_id"]) + " (" + str(pct) + "%)"
            self._add_combo.addItem(label, t["group_id"])

    def _on_add(self):
        gid = self._add_combo.currentData()
        if gid and gid not in self._active_ids:
            self._active_ids.add(gid)
            self._refresh()

    def _on_remove(self):
        gid = self._add_combo.currentData()
        if gid and gid in self._active_ids:
            self._active_ids.discard(gid)
            self._refresh()

    def _rebuild(self):
        self._scene.clear()
        active = [t for t in self._all_trees if t["group_id"] in self._active_ids]
        if not active:
            self._placeholder.setVisible(True)
            self._ctrl_bar.setVisible(False)
            self._view.setVisible(False)
            return
        self._placeholder.setVisible(False)
        self._ctrl_bar.setVisible(True)
        self._view.setVisible(True)
        for col, tree in enumerate(active):
            gid = tree["group_id"]
            prob = tree.get("probability", 0)
            tiers = tree.get("tiers", {})
            for row in range(7):
                tkey = "Tier " + str(row + 1)
                perk_raw = tiers.get(tkey, "")
                if not perk_raw or not perk_raw.strip():
                    continue
                parts = perk_raw.split("\n", 1)
                sname = parts[0].strip()
                sdesc = parts[1].strip() if len(parts) > 1 else ""
                node = SkillNode(gid, TIER_LABELS[row], sname, sdesc, prob, self._icon_provider)
                x = MATRIX_LEFT + col * CELL_W + CELL_W // 2
                y = MATRIX_TOP + row * CELL_H + CELL_H // 2
                node.setPos(x, y)
                self._scene.addItem(node)
        headers = [(t.get("group_name", t["group_id"]), t.get("probability", 0)) for t in active]
        self._view.set_col_headers(headers)
        ncols = len(active)
        scene_w = max(MATRIX_LEFT + ncols * CELL_W + 20, 200)
        scene_h = MATRIX_TOP + 7 * CELL_H + 10
        self._scene.setSceneRect(0, 0, scene_w, scene_h)
        self._view.horizontalScrollBar().setValue(0)
        self._update_combo()

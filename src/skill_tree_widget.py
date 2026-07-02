# -*- coding: utf-8 -*-
"""
skill_tree_widget.py
Skill tree group matrix visualization — with probability halo signature element.
"""

from PySide6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from i18n import t
from perk_zh import get_perk_desc_zh, get_perk_name_zh


# ── shared utility ─────────────────────────────────────────────────
def build_skill_tree_data(gd, results):
    """将正向模拟结果转换为 SkillTreeWidget.set_trees() 所需的数据格式。

    Args:
        gd: GameData 实例
        results: OrderedDict {group_id: probability} 或 None

    Returns:
        list[dict] 或 None（当 results 为 None 时）
    """
    if results is None:
        return None
    trees = []
    for group, prob in results.items():
        if prob <= 0:
            continue
        if gd.group_category(group) == "Always":
            continue
        pt = gd.get_perk_tree(group)
        trees.append({
            "group_id": group,
            "group_name": gd.group_name(group),
            "probability": prob,
            "tiers": pt,
        })
    return trees


def _compute_composition(gd, trees, bg_id):
    """Return set of group_ids for the most likely dice composition.

    Simulates the game's roll logic deterministically:
    - Includes guaranteed exclusive groups (by branch selection)
    - For each non-exclusive category with N rolls, includes the top ceil(N)
      groups by appearance probability
    This mirrors what the game would actually roll in a single instance,
    rather than showing every theoretically possible group.
    """
    bg = gd.backgrounds.get(bg_id, {})
    composition = set()

    # ── 1. Guaranteed exclusive groups ──
    exc_cfg = bg.get("exclusive", {"mode": "none"})
    guaranteed = set()
    if exc_cfg.get("mode") == "fixed":
        guaranteed.add(exc_cfg["group"])
    elif exc_cfg.get("mode") == "prob":
        picks = exc_cfg.get("picks", {})
        if picks:
            best = max(picks, key=picks.get)
            guaranteed.add(best)
    elif exc_cfg.get("mode") == "mixed":
        for g in exc_cfg.get("forced", []):
            guaranteed.add(g)
        picks = exc_cfg.get("picks", {})
        if picks:
            best = max(picks, key=picks.get)
            guaranteed.add(best)
    composition.update(guaranteed)

    # ── 2. Per-category top ceil(num_rolls) non-guaranteed groups ──
    default_rolls = getattr(gd, "default_group_rolls", None)
    if default_rolls is None:
        return composition  # safety: if gd has no roll info, only show guaranteed

    bg_rolls = bg.get("group_rolls", {})

    for cat in ["Shared", "Exclusive", "Weapon", "Armor", "Fighting Style", "Special"]:
        n = default_rolls.get(cat, 0) + bg_rolls.get(cat, 0)
        if n <= 0:
            continue
        n_ceil = int(n + 0.999999)  # ceil, avoiding float precision issues

        cat_groups = [(t["group_id"], t.get("probability", 0))
                      for t in trees
                      if gd.group_category(t["group_id"]) == cat
                      and t["group_id"] not in guaranteed]
        cat_groups.sort(key=lambda x: -x[1])
        for g, _ in cat_groups[:n_ceil]:
            composition.add(g)

    # ── 3. Always include extremely high-probability groups (>90%) ──
    for tree in trees:
        if tree.get("probability", 0) >= 0.90:
            composition.add(tree["group_id"])

    return composition

# ── compact layout constants ─────────────────────────────────────
NODE_RADIUS = 20
NODE_DIAM = NODE_RADIUS * 2
CELL_W = 84
CELL_H = 56
ROW_HEADER_W = 44
COL_HEADER_H = 36
MATRIX_LEFT = ROW_HEADER_W
MATRIX_TOP = COL_HEADER_H
DEFAULT_MAX_GROUPS = 5
HALO_WIDTH = 2.5
HALO_GAP = 3


def _tier_labels(lang="zh"):
    """Return tier label list for given language."""
    return [t("st.tier1"), t("st.tier2"), t("st.tier3"), t("st.tier4"),
            t("st.tier5"), t("st.tier6"), t("st.tier7")]


def prob_fill_color(p):
    if p >= 0.80:
        return QColor("#27704B")
    if p >= 0.50:
        return QColor("#A0522D")
    if p >= 0.20:
        return QColor("#5A6B7D")
    if p > 0:
        return QColor("#8B8378")
    return QColor("#B0B0B0")


def prob_halo_color(p):
    """Halo color slightly lighter than fill."""
    c = prob_fill_color(p)
    return c.lighter(120)


def prob_border_color(p):
    return prob_fill_color(p).darker(130)


class SkillNode(QGraphicsEllipseItem):
    """Skill node: circle + perk icon + probability halo."""
    _current_tooltip = None

    def __init__(self, group_id, tier_label, skill_name, skill_desc,
                 probability, icon_provider=None, highlighted=False, lang="zh"):
        r = NODE_RADIUS
        super().__init__(-r, -r, NODE_DIAM, NODE_DIAM)
        self.group_id = group_id
        self.tier_label = tier_label
        self.skill_name = skill_name
        self.skill_desc = skill_desc
        self._probability = probability
        self._color = prob_fill_color(probability)
        self._halo_color = prob_halo_color(probability)
        self._icon_provider = icon_provider
        self._highlighted = highlighted
        self._lang = lang
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()

    def set_highlighted(self, on):
        self._highlighted = on
        self._apply_style()
        self.update()

    def _apply_style(self):
        if self._highlighted:
            self.setBrush(QBrush(self._color.lighter(130)))
            self.setPen(QPen(QColor("#B8860B"), 2.5))
            self.setOpacity(1.0)
        else:
            self.setBrush(QBrush(self._color))
            self.setPen(QPen(prob_border_color(self._probability), 1.5))
            self.setOpacity(1.0)

    def paint(self, painter, option, widget=None):
        # 1) draw probability halo (outside the node)
        if self._probability > 0:
            halo_r = NODE_RADIUS + HALO_GAP + HALO_WIDTH / 2
            halo_rect = QRectF(-halo_r, -halo_r, halo_r * 2, halo_r * 2)
            arc_len = int(self._probability * 360 * 16)
            if arc_len > 0:
                pen = QPen(self._halo_color, HALO_WIDTH)
                pen.setCapStyle(Qt.RoundCap)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawArc(halo_rect, 90 * 16, -arc_len)

        # 2) draw node body (filled circle + border)
        super().paint(painter, option, widget)

        # 3) draw perk icon (inside the node)
        icon_size = NODE_DIAM - 6
        if self._icon_provider and self.skill_name:
            pix = self._icon_provider.get_perk_icon(self.skill_name, icon_size)
            if pix and not pix.isNull():
                scaled = pix.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                sx = -scaled.width() // 2
                sy = -scaled.height() // 2
                painter.drawPixmap(int(sx), int(sy), scaled)
                return

        # 4) no icon: show perk name abbreviation
        if self.skill_name:
            zh = get_perk_name_zh(self.skill_name)
            abbrev = zh[:2] if len(zh) >= 2 else (self.skill_name[:2].upper() if self.skill_name else "?")
            painter.setPen(QColor("#FFFFFF") if self._probability >= 0.50 else QColor("#1C1814"))
            f = QFont("Microsoft YaHei", 8, QFont.Bold)
            painter.setFont(f)
            painter.drawText(QRectF(-NODE_RADIUS + 2, -NODE_RADIUS + 2,
                                     NODE_DIAM - 4, NODE_DIAM - 4),
                            Qt.AlignCenter, abbrev)

    def _tooltip_text(self):
        if not self.skill_name:
            return ""
        lang = self._lang  # 'zh' or 'en'
        if lang == "en":
            name = self.skill_name
            desc = (self.skill_desc or "").strip()
            lines = [name]
            if desc:
                if len(desc) > 360:
                    desc = desc[:357] + "..."
                lines.append(chr(0x2500) * 24)
                lines.append(desc)
            lines.append("")
            lines.append(f"[{self.group_id}]  {self.tier_label}")
            return "\n".join(lines)
        zh_name = get_perk_name_zh(self.skill_name)
        zh_desc = get_perk_desc_zh(self.skill_name)
        if not zh_desc and self.skill_desc:
            zh_desc = self.skill_desc.strip()
        lines = [zh_name]
        if zh_desc:
            desc = zh_desc.strip()
            if len(desc) > 360:
                desc = desc[:357] + "..."
            lines.append(chr(0x2500) * 24)
            lines.append(desc)
        lines.append("")
        lines.append(f"[{self.group_id}]  {self.tier_label}")
        return "\n".join(lines)

    def hoverEnterEvent(self, event):
        if self.skill_name:
            self.setPen(QPen(QColor("#FFFFFF"), 2.5))
            self._show_tooltip(event.screenPos())
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._hide_tooltip()
        self._apply_style()
        super().hoverLeaveEvent(event)

    def hoverMoveEvent(self, event):
        if SkillNode._current_tooltip and SkillNode._current_tooltip.isVisible():
            sp = event.screenPos()
            SkillNode._current_tooltip.move(int(sp.x()) + 20, int(sp.y()) + 15)
        super().hoverMoveEvent(event)

    def _show_tooltip(self, screen_pos):
        """Show a persistent custom tooltip at the given screen position."""
        # Hide any existing tooltip first
        SkillNode._hide_tooltip()
        tw = QLabel()
        tw.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        tw.setAttribute(Qt.WA_ShowWithoutActivating)
        tw.setStyleSheet(
            "background: #FFFFF0; border: 2px solid #B8860B; "
            "border-radius: 6px; padding: 10px 12px; "
            "font-size: 12px; line-height: 1.6; color: #1C1814;")
        tw.setWordWrap(True)
        tw.setMaximumWidth(420)
        tw.setText(self._tooltip_text())
        tw.adjustSize()
        tw.move(int(screen_pos.x()) + 20, int(screen_pos.y()) + 15)
        tw.show()
        SkillNode._current_tooltip = tw

    @staticmethod
    def _hide_tooltip():
        """Hide and destroy the current tooltip if any."""
        if SkillNode._current_tooltip:
            SkillNode._current_tooltip.hide()
            SkillNode._current_tooltip.deleteLater()
            SkillNode._current_tooltip = None

class ColumnHeaderOverlay(QWidget):
    """Overlay widget for column headers above the QGraphicsView viewport.

    Drawn as a child of SkillTreeView, positioned above viewport margins.
    Uses standard widget painting — avoids drawForeground coordinate pitfalls
    introduced by Qt6's exposed-rect clipping in drawForeground.
    """

    def __init__(self, view, parent=None):
        super().__init__(parent or view)
        self._view = view
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setFixedHeight(COL_HEADER_H)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        w = self.width()

        # ── column header background bar ──
        painter.fillRect(QRectF(0, 0, w, COL_HEADER_H), QColor("#F2F0E8"))
        painter.setPen(QPen(QColor("#D0CCC0"), 1))
        painter.drawLine(QPointF(0, COL_HEADER_H - 1), QPointF(w, COL_HEADER_H - 1))

        # ── top-left corner patch (row header area) ──
        painter.fillRect(QRectF(0, 0, ROW_HEADER_W, COL_HEADER_H), QColor("#E8E4D8"))

        headers = self._view._col_headers
        if not headers:
            painter.end()
            return

        highlight_col = self._view._highlight_col
        flash_count = self._view._flash_count

        painter.setFont(self._view._hdr_font)

        for col, (label, prob) in enumerate(headers):
            # scene → viewport via transform (float-precise, avoids
            # mapFromScene int truncation), then + viewport.x() → overlay coords.
            t = self._view.viewportTransform()
            scene_x = float(MATRIX_LEFT + col * CELL_W)
            vp_x = t.m11() * scene_x + t.m31()
            x = int(self._view.viewport().x() + vp_x)

            # Cull if entirely off-screen
            if x + CELL_W < -CELL_W or x > w + CELL_W:
                continue

            # highlighted column background
            if col == highlight_col:
                alpha = 40 if flash_count % 2 == 0 else 10
                painter.fillRect(
                    QRectF(x, 0, CELL_W, COL_HEADER_H),
                    QColor(184, 134, 11, alpha))

            # probability color block
            pc = prob_fill_color(prob)
            painter.fillRect(QRectF(x + 4, COL_HEADER_H - 10, 5, 6), pc)
            painter.setPen(QPen(pc.darker(130), 1))
            painter.drawRect(QRectF(x + 4, COL_HEADER_H - 10, 5, 6))

            # column name
            text_color = QColor("#B8860B") if col == highlight_col else QColor("#333")
            painter.setPen(text_color)
            painter.drawText(QRectF(x + 12, 2, CELL_W - 16, COL_HEADER_H - 8),
                           Qt.AlignLeft | Qt.AlignVCenter, label)

        painter.end()

class SkillTreeView(QGraphicsView):
    """QGraphicsView with sticky row/column headers."""

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setBackgroundBrush(QColor("#FAFAF6"))

        # Reserve top margin for the column header overlay
        self.setViewportMargins(0, COL_HEADER_H, 0, 0)

        self._col_headers = []
        self._hdr_font = QFont("Microsoft YaHei", 9)
        self._hdr_font.setBold(True)
        self._tier_font = QFont("Microsoft YaHei", 9)
        self._highlight_col = -1
        self._flash_timer = QTimer(self)
        self._flash_timer.timeout.connect(self._on_flash_tick)
        self._flash_count = 0
        self._tier_labels = _tier_labels("zh")
        self.horizontalScrollBar().valueChanged.connect(self._on_h_scroll)

        # Column header overlay — sits above viewport, draws headers with
        # standard QWidget paintEvent (no drawForeground clipping issues).
        self._header_overlay = ColumnHeaderOverlay(self, self)
        self._header_overlay.setGeometry(0, 0, self.width(), COL_HEADER_H)

    def resizeEvent(self, event):
        """Keep column header overlay sized to the full view width."""
        super().resizeEvent(event)
        if hasattr(self, '_header_overlay'):
            self._header_overlay.setGeometry(0, 0, self.width(), COL_HEADER_H)

    def set_col_headers(self, headers):
        self._col_headers = headers
        self.viewport().update()
        if hasattr(self, '_header_overlay'):
            self._header_overlay.update()

    def set_tier_labels(self, labels):
        self._tier_labels = labels

    def highlight_column(self, col_index):
        """Brief flash highlight of a specific column."""
        self._highlight_col = col_index
        self._flash_count = 0
        self._flash_timer.start(150)
        self.viewport().update()
        if hasattr(self, '_header_overlay'):
            self._header_overlay.update()

    def _on_flash_tick(self):
        self._flash_count += 1
        if self._flash_count >= 6:
            self._flash_timer.stop()
            self._highlight_col = -1
        self.viewport().update()
        if hasattr(self, '_header_overlay'):
            self._header_overlay.update()

    def _on_h_scroll(self, value):
        if hasattr(self, '_header_overlay'):
            self._header_overlay.update()
        self.viewport().update()

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if not self._col_headers:
            return
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.setPen(QPen(QColor("#E0DCD0"), 0.5))
        ncols = len(self._col_headers)
        total_w = MATRIX_LEFT + ncols * CELL_W
        total_h = MATRIX_TOP + 7 * CELL_H
        for col in range(ncols + 1):
            x = MATRIX_LEFT + col * CELL_W
            painter.drawLine(x, MATRIX_TOP, x, total_h)
        for row in range(8):
            y = MATRIX_TOP + row * CELL_H
            painter.drawLine(MATRIX_LEFT, y, total_w, y)

    def drawForeground(self, painter, rect):
        """Draw row header labels. Column headers are handled by ColumnHeaderOverlay."""
        super().drawForeground(painter, rect)
        # With viewportMargins, the viewport starts below the overlay at y=0
        vp = self.viewport().rect()
        painter.setRenderHint(QPainter.Antialiasing, False)

        # row header background (viewport height)
        painter.fillRect(QRectF(0, 0, ROW_HEADER_W, vp.height()), QColor("#F2F0E8"))
        painter.setPen(QPen(QColor("#D0CCC0"), 1))
        painter.drawLine(QPointF(ROW_HEADER_W, 0), QPointF(ROW_HEADER_W, vp.height()))

        # tier row labels
        painter.setFont(self._tier_font)
        labels = self._tier_labels
        for row in range(7):
            y = MATRIX_TOP + row * CELL_H
            painter.setPen(QColor("#6B6359"))
            painter.drawText(QRectF(0, y, ROW_HEADER_W, CELL_H),
                           Qt.AlignCenter, labels[row] if row < len(labels) else f"T{row+1}")


class SkillTreeWidget(QWidget):
    """Skill tree matrix: chip bar + QGraphicsView matrix."""

    def __init__(self, parent=None, icon_provider=None):
        super().__init__(parent)
        self._icon_provider = icon_provider
        self._lang = "zh"
        self._all_trees = []
        self._active_ids = set()
        self._scene = QGraphicsScene()
        self._scene.setBackgroundBrush(QColor("#FAFAF6"))
        self._view = SkillTreeView(self._scene)

        # placeholder hint
        self._placeholder = QLabel(t("st.placeholder"))
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet("color: #A09888; font-size: 14px; padding: 30px;")

        # ── Chip bar ──
        self._chip_bar = QWidget()
        self._chip_bar.setVisible(False)
        chip_layout = QHBoxLayout(self._chip_bar)
        chip_layout.setContentsMargins(2, 4, 2, 4)
        chip_layout.setSpacing(4)

        self._chip_label = QLabel(t("st.chip_label"))
        self._chip_label.setStyleSheet("font-size: 12px; color: #6B6359;")
        chip_layout.addWidget(self._chip_label)

        # chip container (scrollable)
        self._chip_scroll = QScrollArea()
        self._chip_scroll.setWidgetResizable(True)
        self._chip_scroll.setFixedHeight(36)
        self._chip_scroll.setFrameShape(QFrame.NoFrame)
        self._chip_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._chip_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._chip_container = QWidget()
        self._chip_layout = QHBoxLayout(self._chip_container)
        self._chip_layout.setContentsMargins(0, 0, 0, 0)
        self._chip_layout.setSpacing(4)
        self._chip_scroll.setWidget(self._chip_container)
        chip_layout.addWidget(self._chip_scroll, 1)

        # "+ Add Group" button
        self._add_btn = QPushButton(t("st.add_btn"))
        self._add_btn.setObjectName("nav_button")
        self._add_btn.setFixedHeight(28)
        self._add_btn.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 2px 10px; "
            "background: transparent; border: 1px dashed #C8BFA8; border-radius: 12px; }"
            "QPushButton:hover { border-color: #B8860B; color: #B8860B; }")
        self._add_btn.clicked.connect(self._on_add_menu)
        chip_layout.addWidget(self._add_btn)

        chip_layout.addStretch()

        # ── Overall layout ──
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._placeholder)
        layout.addWidget(self._chip_bar)
        layout.addWidget(self._view, 1)

    # ── Public API ──────────────────────────────────────────────

    def set_lang(self, lang):
        """Set tooltip display language ('zh' or 'en') and refresh matrix."""
        if lang not in ("zh", "en"):
            lang = "zh"
        self._lang = lang
        # update UI strings
        self._placeholder.setText(t("st.placeholder"))
        self._chip_label.setText(t("st.chip_label"))
        self._add_btn.setText(t("st.add_btn"))
        # update tier labels in view
        self._view.set_tier_labels(_tier_labels(lang))
        self._rebuild()

    def set_trees(self, trees, bg_id=None, gd=None):
        self._all_trees = [t for t in trees if t.get("probability", 0) > 0]
        self._all_trees.sort(key=lambda t: t.get("probability", 0), reverse=True)
        # v0.2.0: show the "actual dice composition" — for each category
        # with N rolls, activate only the top ceil(N) groups by probability,
        # plus guaranteed exclusives.  Users can still add/remove groups
        # manually via the chip bar.
        if bg_id and gd:
            composition = _compute_composition(gd, self._all_trees, bg_id)
            self._active_ids = {t["group_id"] for t in self._all_trees
                                if t["group_id"] in composition}
            # safety: if composition is empty (bug / incomplete data),
            # fall back to showing all groups
            if not self._active_ids and self._all_trees:
                self._active_ids = {t["group_id"] for t in self._all_trees}
        else:
            # backward-compatible fallback: show top 5
            default_n = min(DEFAULT_MAX_GROUPS, len(self._all_trees))
            self._active_ids = {t["group_id"] for t in self._all_trees[:default_n]}
        self._refresh()

    def clear(self):
        self._all_trees = []
        self._active_ids = set()
        self._scene.clear()
        self._view.set_col_headers([])
        self._placeholder.setVisible(True)
        self._chip_bar.setVisible(False)

    def scroll_to_group(self, group_id):
        if group_id not in self._active_ids:
            self._active_ids.add(group_id)
            self._rebuild()
        active = [t for t in self._all_trees if t["group_id"] in self._active_ids]
        for col, tree in enumerate(active):
            if tree["group_id"] == group_id:
                target_x = MATRIX_LEFT + col * CELL_W - 40
                target_x = max(0, target_x)
                self._animate_scroll(target_x)
                self._view.highlight_column(col)
                return

    # ── Internal ──────────────────────────────────────────────────

    def _refresh(self):
        self._rebuild()
        self._rebuild_chips()

    def _rebuild(self):
        self._scene.clear()
        active = [t for t in self._all_trees if t["group_id"] in self._active_ids]
        if not active:
            self._placeholder.setVisible(True)
            self._chip_bar.setVisible(False)
            return
        self._placeholder.setVisible(False)
        self._chip_bar.setVisible(True)

        tier_labels = _tier_labels(self._lang)
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
                tlabel = tier_labels[row] if row < len(tier_labels) else f"Tier {row+1}"
                node = SkillNode(gid, tlabel, sname, sdesc,
                                 prob, self._icon_provider, lang=self._lang)
                x = MATRIX_LEFT + col * CELL_W + CELL_W // 2
                y = MATRIX_TOP + row * CELL_H + CELL_H // 2
                node.setPos(x, y)
                self._scene.addItem(node)

        headers = [(t.get("group_name", t["group_id"]), t.get("probability", 0))
                   for t in active]
        self._view.set_col_headers(headers)
        self._view.viewport().update()  # force repaint so drawForeground picks up new headers
        ncols = len(active)
        scene_w = max(MATRIX_LEFT + ncols * CELL_W + 20, 200)
        scene_h = MATRIX_TOP + 7 * CELL_H + 10
        self._scene.setSceneRect(0, 0, scene_w, scene_h)

    def _rebuild_chips(self):
        """Rebuild chip tag bar."""
        # clear old chips
        for i in reversed(range(self._chip_layout.count())):
            w = self._chip_layout.itemAt(i).widget()
            if w:
                self._chip_layout.removeWidget(w)
                w.deleteLater()

        active = [t for t in self._all_trees if t["group_id"] in self._active_ids]
        for tree in active:
            gid = tree["group_id"]
            prob = tree.get("probability", 0)
            gname = tree.get("group_name", gid)
            pct = int(prob * 100)

            chip = QFrame()
            chip.setFrameShape(QFrame.StyledPanel)
            chip.setStyleSheet(
                "QFrame { background: #F5F0E8; border: 1px solid #DDD6CC; "
                "border-radius: 12px; padding: 2px; }"
                "QFrame:hover { border-color: #C8BFA8; }"
            )
            chip_layout = QHBoxLayout(chip)
            chip_layout.setContentsMargins(8, 1, 4, 1)
            chip_layout.setSpacing(4)

            name_lbl = QLabel(f"{gname} {pct}%")
            name_lbl.setStyleSheet("font-size: 11px; color: #1C1814;")
            chip_layout.addWidget(name_lbl)

            close_btn = QPushButton("×")
            close_btn.setFixedSize(18, 18)
            close_btn.setStyleSheet(
                "QPushButton { font-size: 12px; border: none; background: transparent; "
                "color: #A09888; border-radius: 9px; }"
                "QPushButton:hover { background: #E8D0D0; color: #C0392B; }"
            )
            close_btn.clicked.connect(lambda checked, g=gid: self._remove_group(g))
            chip_layout.addWidget(close_btn)

            self._chip_layout.addWidget(chip)

        self._chip_layout.addStretch()

    def _remove_group(self, group_id):
        self._active_ids.discard(group_id)
        self._refresh()

    def _on_add_menu(self):
        """Show menu to add a group."""
        menu = QMenu(self)
        for tree in self._all_trees:
            if tree["group_id"] in self._active_ids:
                continue
            gname = tree.get("group_name", tree["group_id"])
            pct = int(tree.get("probability", 0) * 100)
            action = menu.addAction(f"{gname}  ({pct}%)")
            action.setData(tree["group_id"])
        if menu.isEmpty():
            menu.addAction(t("st.all_shown")).setEnabled(False)
        chosen = menu.exec(self._add_btn.mapToGlobal(self._add_btn.rect().bottomLeft()))
        if chosen and chosen.data():
            self._active_ids.add(chosen.data())
            self._refresh()

    def _animate_scroll(self, target_x):
        """Smooth scroll to target x position."""
        sb = self._view.horizontalScrollBar()
        anim = QPropertyAnimation(sb, b"value")
        anim.setDuration(300)
        anim.setStartValue(sb.value())
        anim.setEndValue(target_x)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

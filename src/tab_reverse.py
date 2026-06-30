# -*- coding: utf-8 -*-
"""
tab_reverse.py
Reverse derivation page: select target skill tree groups (multi-select), find best
background + trait combinations.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QFont, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem,
    QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QGroupBox, QSpinBox, QMessageBox, QSplitter, QDoubleSpinBox, QComboBox,
    QScrollArea, QFrame, QGridLayout, QDialog, QDialogButtonBox,
)
from i18n import t, cat_name, prob_tier_metal

# Category order and colors
CAT_ORDER = ["Shared", "Exclusive", "Weapon", "Armor", "Fighting Style", "Special"]
CAT_COLOR = {
    "Shared":        "#27704B",
    "Exclusive":     "#8B6914",
    "Weapon":        "#5A6B7D",
    "Armor":         "#7B6B5A",
    "Fighting Style":"#8B1A6B",
    "Special":       "#B8860B",
}


class ReverseTab(QWidget):
    """Reverse derivation page."""

    def __init__(self):
        super().__init__()
        self.gd = None
        self.engine = None
        self.icon_provider = None
        self._cat_panels = {}       # category -> QGroupBox
        self._cat_checkboxes = {}   # category -> list of (QCheckBox, group_id)
        self._last_results = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # ===== LEFT: target selection =====
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setSpacing(8)

        # target group selection area (scrollable)
        self._target_grp = QGroupBox(t("reverse.target_title"))
        target_lv = QVBoxLayout(self._target_grp)
        target_scroll = QScrollArea()
        target_scroll.setWidgetResizable(True)
        target_scroll.setFrameShape(QFrame.NoFrame)
        self._cat_container = QWidget()
        self._cat_layout = QVBoxLayout(self._cat_container)
        self._cat_layout.setSpacing(4)
        self._cat_layout.setContentsMargins(0, 0, 0, 0)
        target_scroll.setWidget(self._cat_container)
        target_lv.addWidget(target_scroll)
        lv.addWidget(self._target_grp, 1)

        # advanced
        self._adv_grp = QGroupBox(t("reverse.advanced"))
        self._adv_grp.setCheckable(True)
        self._adv_grp.setChecked(False)
        adv_form = QFormLayout(self._adv_grp)

        self.multi_trait_check = QCheckBox(t("reverse.multi_trait"))
        adv_form.addRow(self.multi_trait_check)

        self.topn_spin = QSpinBox()
        self.topn_spin.setRange(1, 200)
        self.topn_spin.setValue(20)
        self._topn_label = QLabel(t("reverse.topn_label"))
        adv_form.addRow(self._topn_label, self.topn_spin)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem(t("mode.analytic"), "analytic")
        self.mode_combo.addItem(t("mode.monte_slow"), "monte_carlo")
        self._rev_mode_label = QLabel(t("common.mode_label"))
        adv_form.addRow(self._rev_mode_label, self.mode_combo)

        lv.addWidget(self._adv_grp)

        # derive button
        self.derive_btn = QPushButton(t("reverse.derive_btn"))
        self.derive_btn.setObjectName("primary_btn")
        self.derive_btn.clicked.connect(self._on_derive)
        lv.addWidget(self.derive_btn)

        splitter.addWidget(left)

        # ===== RIGHT: results =====
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)

        self.result_title = QLabel(t("reverse.result_title_ph"))
        self.result_title.setObjectName("page_title")
        rv.addWidget(self.result_title)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-size: 13px; color: #6B6359; padding: 4px;")
        self.summary_label.setWordWrap(True)
        rv.addWidget(self.summary_label)

        self.result_table = QTableWidget(0, 4)
        self._reverse_headers = [
            t("reverse.h_bg"), t("reverse.h_traits"),
            t("reverse.h_score"), t("reverse.h_purity"),
        ]
        self.result_table.setHorizontalHeaderLabels(self._reverse_headers)
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.itemDoubleClicked.connect(self._on_row_double_clicked)
        rv.addWidget(self.result_table, 1)

        # empty result notice
        self.empty_label = QWidget()
        self.empty_label.setObjectName("notice_parchment")
        elv = QVBoxLayout(self.empty_label)
        self._empty_title_lbl = QLabel(t("reverse.empty_title"))
        self._empty_title_lbl.setObjectName("notice_parchment_title")
        elv.addWidget(self._empty_title_lbl)
        self._empty_body_lbl = QLabel(t("reverse.empty_body"))
        self._empty_body_lbl.setWordWrap(True)
        self._empty_body_lbl.setStyleSheet("font-size: 14px; color: #1C1814; padding-top: 4px;")
        elv.addWidget(self._empty_body_lbl)
        self.empty_label.setVisible(False)
        rv.addWidget(self.empty_label)

        splitter.addWidget(right)
        splitter.setSizes([340, 840])
        root.addWidget(splitter, 1)

    # ── data ready ──────────────────────────────────────────────

    def on_data_ready(self, gd, engine, icon_provider):
        self.gd = gd
        self.engine = engine
        self.icon_provider = icon_provider
        self._build_category_panels()
        self.retranslate()

    def retranslate(self):
        """Refresh all static text to current language."""
        self._target_grp.setTitle(t("reverse.target_title"))
        self._adv_grp.setTitle(t("reverse.advanced"))
        self.multi_trait_check.setText(t("reverse.multi_trait"))
        self._topn_label.setText(t("reverse.topn_label"))
        self._rev_mode_label.setText(t("common.mode_label"))
        self.mode_combo.setItemText(0, t("mode.analytic"))
        self.mode_combo.setItemText(1, t("mode.monte_slow"))
        self.derive_btn.setText(t("reverse.derive_btn"))
        self._empty_title_lbl.setText(t("reverse.empty_title"))
        self._empty_body_lbl.setText(t("reverse.empty_body"))
        # result title
        if self._last_results is None:
            self.result_title.setText(t("reverse.result_title_ph"))
        else:
            self._refresh_result_title()
        # table headers
        self._reverse_headers = [
            t("reverse.h_bg"), t("reverse.h_traits"),
            t("reverse.h_score"), t("reverse.h_purity"),
        ]
        self.result_table.setHorizontalHeaderLabels(self._reverse_headers)
        # category panel titles
        for cat, panel in self._cat_panels.items():
            if panel is not None:
                groups = self.gd.groups_by_category(cat) if self.gd else []
                panel.setTitle(f"{cat_name(cat)} ({len(groups)})")
        # re-fill table if results exist
        if self._last_results is not None and self._last_results.get("results"):
            self._fill_table(self._last_results["results"], len(
                [c for cbs in self._cat_checkboxes.values() for cb, _ in cbs if cb.isChecked()]) > 1)

    def _refresh_result_title(self):
        """Rebuild result title from last derive results."""
        targets = []
        for cat, cbs in self._cat_checkboxes.items():
            for cb, gid in cbs:
                if cb.isChecked():
                    targets.append(gid)
        if not targets:
            self.result_title.setText(t("reverse.result_title_ph"))
            return
        title = t("reverse.result_ok_prefix") + " / ".join(self.gd.group_name(t) for t in targets)
        if len(title) > 80:
            title = title[:77] + "..."
        self.result_title.setText(title)

    def _build_category_panels(self):
        """Build 6 category collapsible panels with QCheckBox grids inside."""
        # clear old
        for cat, panel in self._cat_panels.items():
            self._cat_layout.removeWidget(panel)
            panel.deleteLater()
        self._cat_panels.clear()
        self._cat_checkboxes.clear()

        for cat in CAT_ORDER:
            groups = self.gd.groups_by_category(cat)
            if not groups:
                continue
            panel = QGroupBox(f"{cat_name(cat)} ({len(groups)})")
            panel.setCheckable(True)
            panel.setChecked(False)
            panel.setStyleSheet(
                f"QGroupBox::title {{ color: {CAT_COLOR.get(cat, '#333')}; }}"
            )
            grid = QGridLayout(panel)
            grid.setSpacing(3)
            grid.setContentsMargins(8, 16, 8, 8)

            cbs = []
            for i, g in enumerate(groups):
                cb = QCheckBox(self.gd.group_name(g))
                cb.setToolTip(g)
                cb.setProperty("group_id", g)
                cbs.append((cb, g))
                row, col = divmod(i, 2)
                grid.addWidget(cb, row, col)

            self._cat_checkboxes[cat] = cbs
            self._cat_panels[cat] = panel
            self._cat_layout.addWidget(panel)
        self._cat_layout.addStretch()

    # ── derive ──────────────────────────────────────────────────

    def _on_derive(self):
        if self.gd is None or self.engine is None:
            return

        # collect all checked target groups
        targets = []
        for cat, cbs in self._cat_checkboxes.items():
            for cb, gid in cbs:
                if cb.isChecked():
                    targets.append(gid)

        if not targets:
            QMessageBox.warning(self, t("reverse.need_target_title"),
                                t("reverse.need_target_body"))
            return

        multi_trait = self.multi_trait_check.isChecked()
        top_n = self.topn_spin.value()
        mode = self.mode_combo.currentData()

        try:
            rd = self.engine.reverse_derive(
                targets, mode=mode, multi_trait=multi_trait, max_traits=2,
                top_n=top_n, tiebreak_limit=20)
        except Exception as e:
            QMessageBox.critical(self, t("reverse.err_title"),
                                 t("reverse.err_prefix") + str(e))
            return

        self._last_results = rd
        self.empty_label.setVisible(False)
        self.result_table.setVisible(True)

        if not rd["results"]:
            self.result_table.setRowCount(0)
            self.result_title.setText(t("reverse.result_none"))
            self.empty_label.setVisible(True)
            self.summary_label.setText("")
            self._last_results = None
            return

        multi = len(targets) > 1
        title = t("reverse.result_ok_prefix") + " / ".join(self.gd.group_name(t) for t in targets)
        if len(title) > 80:
            title = title[:77] + "..."
        self.result_title.setText(title)

        tiebreak = rd.get("tiebreak_used", False)
        summary_parts = [
            t("reverse.summary_max") + f"<b>{rd['max_score']:.4f}</b>",
            t("reverse.summary_tied").format(rd['tied_count']),
            t("reverse.summary_returned").format(len(rd['results'])),
        ]
        if tiebreak:
            summary_parts.append(t("reverse.summary_noise"))
        self.summary_label.setText("　".join(summary_parts))
        self._fill_table(rd["results"], multi)

    def _fill_table(self, results, multi):
        self.result_table.setRowCount(len(results))
        data_font = QFont("Consolas", 11)
        data_font.setStyleHint(QFont.Monospace)

        for row, (bg, traits, score, probs, purity) in enumerate(results):
            # background col: icon + display name
            bg_text = self.gd.bg_name(bg)
            bg_item = QTableWidgetItem(f"  {bg_text}  ({bg})")
            if self.icon_provider:
                bg_item.setIcon(self.icon_provider.get_icon(bg, "backgrounds", 24))
            self.result_table.setItem(row, 0, bg_item)

            # traits col
            trait_text = ", ".join(self.gd.trait_name(t) for t in traits) if traits else t("common.no_traits")
            self.result_table.setItem(row, 1, QTableWidgetItem(trait_text))

            # prob/score col
            if multi:
                prob_str = f"{score:.3f}  (" + ", ".join(
                    f"{self.gd.group_name(k)[:4]}={v*100:.0f}%" for k, v in probs.items()) + ")"
            else:
                g = list(probs.keys())[0]
                prob_str = f"{probs[g]*100:.1f}%"
            prob_item = QTableWidgetItem(prob_str)
            prob_item.setFont(data_font)
            prob_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 2, prob_item)

            # purity col (with color coding)
            purity_item = QTableWidgetItem(f"{purity:.2f}")
            purity_item.setTextAlignment(Qt.AlignCenter)
            if purity <= 0.5:
                purity_item.setBackground(QBrush(QColor("#E0F0E0")))
                purity_item.setToolTip(t("reverse.purity_low_tip"))
            elif purity > 2.0:
                purity_item.setBackground(QBrush(QColor("#F0E0E0")))
                purity_item.setToolTip(t("reverse.purity_high_tip"))
            self.result_table.setItem(row, 3, purity_item)

            self.result_table.setRowHeight(row, 36)

    def _on_row_double_clicked(self, item):
        """Double-click row → popup showing forward simulation detail distribution."""
        row = item.row()
        bg_item = self.result_table.item(row, 0)
        trait_item = self.result_table.item(row, 1)
        if not bg_item or not trait_item:
            return

        # extract bg_id from background text
        bg_text = bg_item.text().strip()
        # format: "  display_name  (bg_id)"
        if "(" in bg_text and bg_text.endswith(")"):
            bg_id = bg_text[bg_text.rindex("(") + 1:-1]
        else:
            return

        trait_text = trait_item.text().strip()
        trait_ids = []
        no_traits_text = t("common.no_traits")
        if trait_text != no_traits_text:
            for tname in trait_text.split(", "):
                tname = tname.strip()
                for tid in self.gd.traits:
                    if self.gd.trait_name(tid) == tname:
                        trait_ids.append(tid)
                        break

        try:
            res = self.engine.forward_simulate(bg_id, trait_ids, mode="analytic")
        except Exception:
            return

        if res is None:
            QMessageBox.information(self, t("reverse.dlg_none_title"),
                                    t("reverse.dlg_none_body"))
            return

        # popup dialog
        dlg = QDialog(self)
        dlg.setWindowTitle(t("reverse.dlg_title_prefix") + self.gd.bg_name(bg_id))
        dlg.resize(550, 500)
        dlv = QVBoxLayout(dlg)

        info = QLabel(t("reverse.dlg_bg_label") + self.gd.bg_name(bg_id) + "\n"
                      + t("reverse.dlg_traits_label")
                      + (", ".join(self.gd.trait_name(t) for t in trait_ids) if trait_ids else t("common.no_traits")))
        info.setStyleSheet("font-size: 14px; font-weight: bold; padding: 8px;")
        dlv.addWidget(info)

        tbl = QTableWidget(0, 3)
        tbl.setHorizontalHeaderLabels([
            t("reverse.dlg_h_group"), t("reverse.dlg_h_category"), t("reverse.dlg_h_prob")])
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tbl.verticalHeader().setVisible(False)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setAlternatingRowColors(True)

        items = [(g, p) for g, p in res.items() if p > 0]
        tbl.setRowCount(len(items))
        for i, (g, p) in enumerate(items):
            tbl.setItem(i, 0, QTableWidgetItem(self.gd.group_name(g)))
            cat = self.gd.group_category(g) or ""
            tbl.setItem(i, 1, QTableWidgetItem(cat_name(cat) if cat else cat))
            label_text, color, _ = prob_tier_metal(p)
            prob_item = QTableWidgetItem(f"{p*100:.1f}%  ({label_text})")
            prob_item.setForeground(QBrush(QColor(color)))
            prob_item.setTextAlignment(Qt.AlignCenter)
            tbl.setItem(i, 2, prob_item)

        dlv.addWidget(tbl, 1)

        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dlg.accept)
        dlv.addWidget(btns)

        dlg.exec()

# -*- coding: utf-8 -*-
"""
tab_builds.py
Build recommendations page: auto analysis + custom build files (builds/*.txt).
"""

import os
import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from build_parser import create_example_file, generate_template, scan_builds
from i18n import t
from skill_tree_widget import SkillTreeWidget, build_skill_tree_data


def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class BuildsTab(QWidget):
    """Build recommendations page."""

    def __init__(self):
        super().__init__()
        self.gd = None
        self.engine = None
        self.icon_provider = None
        self._last_results = None
        self._current_bg_id = None
        self._builds_data = []          # list of BuildData
        self._build_tag_btns = []       # QPushButton for each build
        self._current_build_idx = -1

        self._build_ui()

    # ── UI construction ──────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # ── LEFT: background list ──
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setSpacing(6)

        self._bg_label = QLabel(t("builds.bg_label"))
        self._bg_label.setObjectName("section_title")
        lv.addWidget(self._bg_label)

        self.bg_list = QListWidget()
        self.bg_list.currentItemChanged.connect(self._on_bg_changed)
        lv.addWidget(self.bg_list, 1)

        splitter.addWidget(left)

        # ── RIGHT: content area ──
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(8)

        # title
        self.title = QLabel("")
        self.title.setObjectName("page_title")
        rv.addWidget(self.title)

        # ── custom build section ──
        self.custom_section = QWidget()
        self.custom_section.setVisible(False)
        cv = QVBoxLayout(self.custom_section)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(6)

        # build tag bar
        tag_bar = QWidget()
        tag_layout = QHBoxLayout(tag_bar)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(4)

        self._build_tag_lbl = QLabel(t("builds.custom_label"))
        self._build_tag_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #6B6359;")
        tag_layout.addWidget(self._build_tag_lbl)

        self.tag_scroll = QScrollArea()
        self.tag_scroll.setWidgetResizable(True)
        self.tag_scroll.setFixedHeight(36)
        self.tag_scroll.setFrameShape(QFrame.NoFrame)
        self.tag_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tag_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tag_container = QWidget()
        self.tag_layout_inner = QHBoxLayout(self.tag_container)
        self.tag_layout_inner.setContentsMargins(0, 0, 0, 0)
        self.tag_layout_inner.setSpacing(3)
        self.tag_scroll.setWidget(self.tag_container)
        tag_layout.addWidget(self.tag_scroll, 1)

        # button group
        self.new_btn = QPushButton(t("builds.new_btn"))
        self.new_btn.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 2px 10px; "
            "background: transparent; border: 1px dashed #C8BFA8; border-radius: 12px; }"
            "QPushButton:hover { border-color: #B8860B; color: #B8860B; }")
        self.new_btn.clicked.connect(self._on_new_build)
        tag_layout.addWidget(self.new_btn)

        self.edit_btn = QPushButton(t("builds.edit_btn"))
        self.edit_btn.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 2px 8px; "
            "background: transparent; border: 1px solid #DDD6CC; border-radius: 4px; }"
            "QPushButton:hover { border-color: #C8BFA8; }")
        self.edit_btn.clicked.connect(self._on_edit_build)
        tag_layout.addWidget(self.edit_btn)

        self.folder_btn = QPushButton("📂")
        self.folder_btn.setToolTip(t("builds.folder_tip"))
        self.folder_btn.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 2px 6px; "
            "background: transparent; border: 1px solid #DDD6CC; border-radius: 4px; }"
            "QPushButton:hover { border-color: #C8BFA8; }")
        self.folder_btn.clicked.connect(self._on_open_folder)
        tag_layout.addWidget(self.folder_btn)

        cv.addWidget(tag_bar)

        # build detail
        self.build_detail = QWidget()
        self.build_detail.setObjectName("card")
        bdv = QVBoxLayout(self.build_detail)
        bdv.setSpacing(8)

        # recommended traits hint
        self.build_traits_hint = QLabel("")
        self.build_traits_hint.setStyleSheet(
            "font-size: 12px; color: #8B6914; background: #FDF8F0; "
            "padding: 4px 10px; border-radius: 4px; font-weight: bold;")
        self.build_traits_hint.setVisible(False)
        bdv.addWidget(self.build_traits_hint)

        # 10-point perk table
        self.perk_table = QTableWidget(0, 5)
        self._perk_headers = [
            t("builds.perk_h_num"), t("builds.perk_h_group"),
            t("builds.perk_h_tier"), t("builds.perk_h_perk"),
            t("builds.perk_h_prob"),
        ]
        self.perk_table.setHorizontalHeaderLabels(self._perk_headers)
        self.perk_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.perk_table.horizontalHeader().resizeSection(0, 30)
        self.perk_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.perk_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.perk_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.perk_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.perk_table.verticalHeader().setVisible(False)
        self.perk_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.perk_table.setMaximumHeight(380)
        bdv.addWidget(self.perk_table)

        # playstyle suggestions
        self.playstyle_text = QLabel("")
        self.playstyle_text.setWordWrap(True)
        self.playstyle_text.setStyleSheet(
            "font-size: 12px; color: #1C1814; padding: 8px; "
            "background: #FAFAF6; border-radius: 4px; line-height: 1.6;")
        self.playstyle_text.setVisible(False)
        bdv.addWidget(self.playstyle_text)

        cv.addWidget(self.build_detail)
        rv.addWidget(self.custom_section)

        # ── auto analysis section ──
        self._auto_title = QLabel(t("builds.auto_title"))
        self._auto_title.setObjectName("section_title")
        rv.addWidget(self._auto_title)

        self.auto_cards = QWidget()
        ac_layout = QHBoxLayout(self.auto_cards)
        ac_layout.setSpacing(10)
        ac_layout.setContentsMargins(0, 0, 0, 0)

        # three cards
        self._card_defense = self._make_auto_card(t("builds.card_defense"), "defense")
        self._card_offense = self._make_auto_card(t("builds.card_offense"), "offense")
        self._card_special = self._make_auto_card(t("builds.card_special"), "special")
        ac_layout.addWidget(self._card_defense, 1)
        ac_layout.addWidget(self._card_offense, 1)
        ac_layout.addWidget(self._card_special, 1)

        rv.addWidget(self.auto_cards)

        # ── guide hint (when no custom builds) ──
        self.guide_hint = QLabel(t("builds.guide"))
        self.guide_hint.setStyleSheet(
            "font-size: 12px; color: #6B6359; padding: 6px 12px; "
            "background: #F5F0E8; border-radius: 4px;")
        self.guide_hint.setVisible(False)
        rv.addWidget(self.guide_hint)

        # ── skill tree matrix ──
        self.skill_tree = SkillTreeWidget(icon_provider=self.icon_provider)
        rv.addWidget(self.skill_tree, 1)

        splitter.addWidget(right)
        splitter.setSizes([280, 900])
        root.addWidget(splitter, 1)

    def _make_auto_card(self, title_text, card_id):
        card = QFrame()
        card.setObjectName("card")
        clv = QVBoxLayout(card)
        clv.setSpacing(4)
        title = QLabel(title_text)
        title.setObjectName("section_title")
        clv.addWidget(title)
        content = QLabel(t("builds.card_ph"))
        content.setWordWrap(True)
        content.setStyleSheet("font-size: 12px; color: #6B6359; line-height: 1.5;")
        content.setMinimumHeight(60)
        clv.addWidget(content, 1)
        card.setProperty("card_content", content)
        setattr(self, f"_card_title_{card_id}", title)
        setattr(self, f"_card_content_{card_id}", content)
        return card

    # ── retranslate ──────────────────────────────────────────────

    def retranslate(self):
        """Refresh all static text to current language."""
        self._bg_label.setText(t("builds.bg_label"))
        self._build_tag_lbl.setText(t("builds.custom_label"))
        self.new_btn.setText(t("builds.new_btn"))
        self.edit_btn.setText(t("builds.edit_btn"))
        self.folder_btn.setToolTip(t("builds.folder_tip"))
        self._auto_title.setText(t("builds.auto_title"))
        # auto card titles
        for card_id in ["defense", "offense", "special"]:
            title_lbl = getattr(self, f"_card_title_{card_id}", None)
            if title_lbl:
                title_lbl.setText(t(f"builds.card_{card_id}"))
        self.guide_hint.setText(t("builds.guide"))
        # perk table headers
        self._perk_headers = [
            t("builds.perk_h_num"), t("builds.perk_h_group"),
            t("builds.perk_h_tier"), t("builds.perk_h_perk"),
            t("builds.perk_h_prob"),
        ]
        self.perk_table.setHorizontalHeaderLabels(self._perk_headers)
        # page title
        if self._current_bg_id and self.gd:
            self.title.setText(t("builds.page_title_prefix") + self.gd.bg_name(self._current_bg_id))
        # refresh auto cards
        if self._last_results is not None:
            self._refresh_auto_cards(self._last_results)
        # refresh current build detail
        if self._current_build_idx >= 0 and self._current_build_idx < len(self._builds_data):
            self._show_build_detail(self._builds_data[self._current_build_idx])

    # ── data ready ──────────────────────────────────────────────

    def on_data_ready(self, gd, engine, icon_provider):
        self.gd = gd
        self.engine = engine
        self.icon_provider = icon_provider
        self.skill_tree._icon_provider = icon_provider

        self.bg_list.clear()
        for bg_id in gd.filtered_complete_backgrounds():
            item = QListWidgetItem(gd.bg_name(bg_id))
            item.setData(Qt.UserRole, bg_id)
            self.bg_list.addItem(item)
        if self.bg_list.count() > 0:
            self.bg_list.setCurrentRow(0)

        # sync skill tree language, refresh tooltip if results exist
        self.skill_tree.set_lang(getattr(gd, "lang", "zh"))
        if self._last_results:
            self._fill_skill_tree(self._last_results)

        self.retranslate()

    # ── background switch ────────────────────────────────────────

    def _on_bg_changed(self, current, previous):
        if current is None or self.gd is None or self.engine is None:
            return
        bg_id = current.data(Qt.UserRole)
        self._current_bg_id = bg_id
        self.title.setText(t("builds.page_title_prefix") + self.gd.bg_name(bg_id))

        # forward simulate
        try:
            res = self.engine.forward_simulate(bg_id, [], mode="analytic")
        except Exception:
            res = None
        self._last_results = res

        # load custom builds for this background
        self._load_builds(bg_id)

        # refresh auto analysis cards
        self._refresh_auto_cards(res)

        # refresh skill tree
        self._fill_skill_tree(res)

    # ── auto analysis cards ──────────────────────────────────────

    def _refresh_auto_cards(self, results):
        if results is None:
            for card_id in ["defense", "offense", "special"]:
                lbl = getattr(self, f"_card_content_{card_id}", None)
                if lbl:
                    lbl.setText(t("builds.card_none"))
            return

        # defense core: armor + shield + general survival
        defense_groups = {"Heavy Armor", "Medium Armor", "Light Armor", "Shield",
                          "Tough", "Unstoppable", "Agile", "Fast", "Trained", "Vigorous"}
        self._fill_card("defense", results, defense_groups)

        # offense direction: weapons + fighting styles
        offense_groups = {"Axe", "Bow", "Cleaver", "Crossbow", "Dagger", "Flail",
                          "Hammer", "Mace", "Polearm", "Spear", "Sword", "Throwing",
                          "Cross", "Whip",
                          "Swift", "Power", "Mighty Blow", "Deft Blow", "Melee Fighting Style",
                          "Ranged", "Ranged Fighting Style", "Shield Fighting Style"}
        self._fill_card("offense", results, offense_groups)

        # special potential: exclusive + special + low-prob but valuable
        special_groups = set()
        for g in self.gd.groups:
            cat = self.gd.group_category(g)
            if cat in ("Exclusive", "Special"):
                special_groups.add(g)
        special_groups.update({"Back to Basics", "Tactician"})
        self._fill_card("special", results, special_groups)

    def _fill_card(self, card_id, results, group_set):
        lbl = getattr(self, f"_card_content_{card_id}", None)
        if lbl is None:
            return

        relevant = []
        for g, p in results.items():
            if g in group_set and p > 0:
                relevant.append((g, p))
        relevant.sort(key=lambda x: -x[1])
        top10 = relevant[:10]

        if not top10:
            lbl.setText(t("builds.card_empty"))
            return

        html_parts = []
        for g, p in top10:
            gname = self.gd.group_name(g)
            pct = int(p * 100)
            if p >= 0.80:
                color = "#27704B"
            elif p >= 0.50:
                color = "#A0522D"
            elif p >= 0.20:
                color = "#5A6B7D"
            else:
                color = "#8B8378"
            html_parts.append(
                f"<span style='display:inline-block; margin:2px 4px; padding:2px 6px; "
                f"border:1px solid {color}; border-radius:4px; font-size:11px; "
                f"color:{color};'>{gname} {pct}%</span>"
            )
        lbl.setText("".join(html_parts))

    # ── custom builds ────────────────────────────────────────────

    def _get_builds_dir(self):
        return os.path.join(_app_dir(), "builds")

    def _load_builds(self, bg_id):
        """Load custom build files matching current background."""
        builds_dir = self._get_builds_dir()

        # first launch: create example file (failure shouldn't block the tab)
        try:
            create_example_file(builds_dir, lang=getattr(self.gd, "lang", "zh"))
        except Exception:
            pass

        all_builds = scan_builds(builds_dir)
        self._builds_data = [b for b in all_builds
                             if b.background == bg_id and b.is_valid()]

        # rebuild tag bar
        self._rebuild_tag_bar()

        if self._builds_data:
            self.custom_section.setVisible(True)
            self.guide_hint.setVisible(False)
            self._select_build(0)
        else:
            self.custom_section.setVisible(False)
            self.guide_hint.setVisible(True)
            self._clear_build_detail()
            self._current_build_idx = -1

    def _rebuild_tag_bar(self):
        # clear old
        for btn in self._build_tag_btns:
            self.tag_layout_inner.removeWidget(btn)
            btn.deleteLater()
        self._build_tag_btns.clear()

        for i, bd in enumerate(self._builds_data):
            btn = QPushButton(bd.name)
            btn.setCheckable(True)
            btn.setStyleSheet(
                "QPushButton { font-size: 11px; padding: 3px 10px; "
                "background: #F5F0E8; border: 1px solid #DDD6CC; border-radius: 12px; }"
                "QPushButton:hover { border-color: #C8BFA8; }"
                "QPushButton:checked { background: #B8860B; color: #FFFFFF; "
                "border-color: #9A6F09; }")
            btn.clicked.connect(lambda checked, idx=i: self._select_build(idx))
            self._build_tag_btns.append(btn)
            self.tag_layout_inner.addWidget(btn)
        self.tag_layout_inner.addStretch()

    def _select_build(self, idx):
        if idx < 0 or idx >= len(self._builds_data):
            return
        self._current_build_idx = idx
        bd = self._builds_data[idx]

        # update tag checked state
        for i, btn in enumerate(self._build_tag_btns):
            btn.setChecked(i == idx)

        self._show_build_detail(bd)

    def _show_build_detail(self, bd):
        """Display build detail on the right side."""
        # recommended traits hint
        if bd.traits:
            trait_zh = []
            for tid in bd.traits:
                tname = self.gd.trait_name(tid) if self.gd else tid
                trait_zh.append(tname)
            self.build_traits_hint.setText(t("builds.traits_hint_prefix") + ", ".join(trait_zh))
            self.build_traits_hint.setVisible(True)
        else:
            self.build_traits_hint.setVisible(False)

        # perk table
        self.perk_table.setRowCount(len(bd.perks))
        data_font = QFont("Consolas", 11)
        data_font.setStyleHint(QFont.Monospace)

        for row, (order, group, tier, perk_name) in enumerate(bd.perks):
            # order number
            order_item = QTableWidgetItem(str(order))
            order_item.setTextAlignment(Qt.AlignCenter)
            self.perk_table.setItem(row, 0, order_item)

            # skill tree group
            gname = self.gd.group_name(group) if self.gd else group
            self.perk_table.setItem(row, 1, QTableWidgetItem(gname))

            # tier
            self.perk_table.setItem(row, 2, QTableWidgetItem(tier))

            # perk name
            self.perk_table.setItem(row, 3, QTableWidgetItem(perk_name))

            # probability for this group under current background
            prob = 0
            if self._last_results and group in self._last_results:
                prob = self._last_results[group]
            prob_item = QTableWidgetItem(f"{prob*100:.1f}%")
            prob_item.setFont(data_font)
            prob_item.setTextAlignment(Qt.AlignCenter)

            if prob < 0.20 and prob > 0:
                prob_item.setForeground(QBrush(QColor("#C0392B")))
                tip = t("builds.perk_low_tip").replace("{group}", gname)
                prob_item.setToolTip(tip)
                prob_item.setText(f"{prob*100:.1f}% ⚠")
            elif prob >= 0.80:
                prob_item.setForeground(QBrush(QColor("#27704B")))
            self.perk_table.setItem(row, 4, prob_item)

            self.perk_table.setRowHeight(row, 28)

        # Playstyle
        if bd.playstyle.strip():
            self.playstyle_text.setText(bd.playstyle.strip())
            self.playstyle_text.setVisible(True)
        else:
            self.playstyle_text.setVisible(False)

        # Parse errors
        if bd.parse_errors:
            err_text = t("builds.parse_err_prefix") + "\n" + "\n".join(bd.parse_errors[:5])
            self.playstyle_text.setText(err_text)
            self.playstyle_text.setStyleSheet(
                "font-size: 11px; color: #C0392B; padding: 8px; "
                "background: #FDF0F0; border-radius: 4px;")
            self.playstyle_text.setVisible(True)

    def _clear_build_detail(self):
        self.build_traits_hint.setVisible(False)
        self.perk_table.setRowCount(0)
        self.playstyle_text.setVisible(False)

    # ── button events ────────────────────────────────────────────

    def _on_new_build(self):
        if not self._current_bg_id:
            return
        name = self.gd.bg_name(self._current_bg_id) if self.gd else self._current_bg_id
        builds_dir = self._get_builds_dir()
        filepath = generate_template(self._current_bg_id, name, builds_dir, lang=getattr(self.gd, "lang", "zh"))

        # try to open with system editor
        try:
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", filepath])
            else:
                subprocess.Popen(["xdg-open", filepath])
        except Exception:
            QMessageBox.information(self, t("builds.file_created_title"),
                                    t("builds.file_created_body").replace("{path}", filepath))

        # reload
        self._load_builds(self._current_bg_id)

    def _on_edit_build(self):
        """Edit the currently selected build file."""
        if not self._builds_data or self._current_build_idx < 0:
            return
        if self._current_build_idx < len(self._builds_data):
            bd = self._builds_data[self._current_build_idx]
            filepath = os.path.join(self._get_builds_dir(), bd.filename)
            try:
                if sys.platform == "win32":
                    os.startfile(filepath)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", filepath])
                else:
                    subprocess.Popen(["xdg-open", filepath])
            except Exception:
                QMessageBox.warning(self, t("builds.open_err_title"),
                                    t("builds.open_err_body") + filepath)

    def _on_open_folder(self):
        builds_dir = self._get_builds_dir()
        os.makedirs(builds_dir, exist_ok=True)
        try:
            if sys.platform == "win32":
                os.startfile(builds_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", builds_dir])
            else:
                subprocess.Popen(["xdg-open", builds_dir])
        except Exception:
            QMessageBox.warning(self, t("builds.open_folder_err_title"),
                                t("builds.open_folder_err_body") + builds_dir)

    # ── skill tree matrix ────────────────────────────────────────

    def _fill_skill_tree(self, results):
        trees = build_skill_tree_data(self.gd, results)
        if trees is None:
            self.skill_tree.clear()
        else:
            self.skill_tree.set_trees(trees, bg_id=self._current_bg_id, gd=self.gd)

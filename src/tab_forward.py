# -*- coding: utf-8 -*-
"""tab_forward.py - forward simulation page."""

from PySide6.QtCore import QStringListModel, Qt
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QCompleter,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from i18n import cat_name, prob_tier_label, t
from skill_tree_widget import SkillTreeWidget, build_skill_tree_data

# Category display colors (visual only, not language-specific)
CAT_COLOR = {
    "Shared":("#27704B","#FFFFFF"),"Exclusive":("#8B6914","#FFFFFF"),
    "Weapon":("#5A6B7D","#FFFFFF"),"Armor":("#7B6B5A","#FFFFFF"),
    "Fighting Style":("#8B1A6B","#FFFFFF"),"Special":("#B8860B","#FFFFFF"),
    "Always":("#4A4A4A","#FFFFFF"),
}

# v0.3.0: Attribute key mapping for i18n
_ATTR_I18N = {
    "Hitpoints": "attr.hitpoints",
    "Fatigue": "attr.fatigue",
    "Bravery": "attr.bravery",
    "Initiative": "attr.initiative",
    "Melee Skill": "attr.melee_skill",
    "Ranged Skill": "attr.ranged_skill",
    "Melee Defense": "attr.melee_defense",
    "Ranged Defense": "attr.ranged_defense",
}

# Fixed order for attribute display
_ATTR_ORDER = [
    "Hitpoints", "Fatigue", "Bravery", "Initiative",
    "Melee Skill", "Ranged Skill", "Melee Defense", "Ranged Defense",
]


class ForwardTab(QWidget):
    TRAIT_COLS = 4

    def __init__(self):
        super().__init__()
        self.gd = None
        self.engine = None
        self.icon_provider = None
        self._last_results = None
        self._trait_checkboxes = []
        self._talent_stars = {}  # v0.3.0: manual star overrides
        self._star_combos = {}    # v0.3.0: {attr: QComboBox}
        self._star_labels = {}    # v0.3.0: {attr: QLabel} for retranslate
        self._attr_bars = {}      # v0.3.0: {attr: (name_QLabel, value_QLabel)}
        self._gathering_stars = False  # v0.3.0: guard for programmatic star changes
        self._attr_est_label = None
        self._attr_miss_label = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # ===== LEFT =====
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setSpacing(8)

        # bg group
        self._bg_grp = QGroupBox(t("forward.char_config"))
        bf = QFormLayout(self._bg_grp)
        bf.setSpacing(8)

        self.bg_combo = QComboBox()
        self.bg_combo.setEditable(True)
        self.bg_combo.setInsertPolicy(QComboBox.NoInsert)
        self.bg_combo.lineEdit().setPlaceholderText(t("forward.bg_search_ph"))
        self.bg_combo.lineEdit().setClearButtonEnabled(True)
        self._bg_model = QStringListModel()
        self._bg_completer = QCompleter()
        self._bg_completer.setModel(self._bg_model)
        self._bg_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._bg_completer.setFilterMode(Qt.MatchContains)
        self.bg_combo.setCompleter(self._bg_completer)
        self.bg_combo.currentIndexChanged.connect(self._on_bg_changed)  # v0.3.0
        self._bg_label = QLabel(t("forward.bg_label"))
        bf.addRow(self._bg_label, self.bg_combo)

        # traits section
        self._trait_label = QLabel(t("forward.traits_label"))
        self._trait_label.setStyleSheet("font-weight:bold;")
        bf.addRow(self._trait_label)

        # trait search filter
        self.trait_search = QLineEdit()
        self.trait_search.setPlaceholderText(t("forward.trait_search_ph"))
        self.trait_search.setClearButtonEnabled(True)
        self.trait_search.setStyleSheet(
            "QLineEdit { padding: 4px 8px; border: 1px solid #DDD6CC; "
            "border-radius: 4px; background: #FFFEF9; font-size: 12px; }")
        self.trait_search.textChanged.connect(self._on_trait_search)
        bf.addRow(self.trait_search)

        lv.addWidget(self._bg_grp)

        # trait grid in its own scroll area
        self.trait_scroll = QScrollArea()
        self.trait_scroll.setWidgetResizable(True)
        self.trait_scroll.setFrameShape(QFrame.NoFrame)
        self.trait_scroll.setMinimumHeight(100)
        self.trait_container = QWidget()
        self.trait_grid = QGridLayout(self.trait_container)
        self.trait_grid.setSpacing(2)
        self.trait_grid.setContentsMargins(4, 4, 4, 4)
        self.trait_scroll.setWidget(self.trait_container)
        lv.addWidget(self.trait_scroll, 1)

        # advanced
        self._adv_grp = QGroupBox(t("forward.advanced"))
        self._adv_grp.setCheckable(True)
        self._adv_grp.setChecked(False)
        af = QFormLayout(self._adv_grp)
        self.attr_check = QCheckBox(t("forward.use_attr"))
        self.attr_check.setChecked(True)
        self.attr_check.toggled.connect(self._on_attr_toggled)  # v0.3.0
        self.proj_check = QCheckBox(t("forward.use_proj"))
        self.proj_check.setChecked(True)
        af.addRow(self.attr_check)
        af.addRow(self.proj_check)

        # v0.3.0: Star adjustment controls inside advanced panel
        self._star_grp = QWidget()
        star_layout = QGridLayout(self._star_grp)
        star_layout.setSpacing(2)
        star_layout.setContentsMargins(0, 4, 0, 0)
        for i, attr in enumerate(_ATTR_ORDER):
            lbl = QLabel(t(_ATTR_I18N[attr]))
            lbl.setObjectName("starLabel")
            self._star_labels[attr] = lbl
            star_layout.addWidget(lbl, i, 0)
            combo = QComboBox()
            combo.setObjectName("starCombo")
            for s in range(4):
                combo.addItem(t(f"star.{s}"), s)
            combo.setCurrentIndex(1)  # default 1 star
            combo.currentIndexChanged.connect(self._on_star_changed)
            self._star_combos[attr] = combo
            star_layout.addWidget(combo, i, 1)
        af.addRow(self._star_grp)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem(t("mode.analytic"), "analytic")
        self.mode_combo.addItem(t("mode.monte"), "monte_carlo")
        self._mode_label = QLabel(t("common.mode_label"))
        af.addRow(self._mode_label, self.mode_combo)
        lv.addWidget(self._adv_grp)

        # calc button
        self.calc_btn = QPushButton(t("forward.calc_btn"))
        self.calc_btn.setObjectName("primary_btn")
        self.calc_btn.clicked.connect(self._on_calculate)
        lv.addWidget(self.calc_btn)

        splitter.addWidget(left)

        # ===== RIGHT =====
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0,0,0,0)

        self.result_title = QLabel(t("forward.result_title_ph"))
        self.result_title.setObjectName("page_title")
        rv.addWidget(self.result_title)

        self.none_label = QWidget()
        self.none_label.setObjectName("notice_parchment")
        nlv = QVBoxLayout(self.none_label)
        self._none_title_lbl = QLabel(t("forward.none_title"))
        self._none_title_lbl.setObjectName("notice_parchment_title")
        nlv.addWidget(self._none_title_lbl)
        self.none_reason = QLabel("")
        self.none_reason.setWordWrap(True)
        self.none_reason.setStyleSheet("font-size:14px;color:#1C1814;padding-top:4px;")
        nlv.addWidget(self.none_reason)
        self.none_label.setVisible(False)
        rv.addWidget(self.none_label)

        self.inner_splitter = QSplitter(Qt.Vertical)
        self.inner_splitter.setVisible(False)

        # v0.3.0: Attribute range panel — compact 2-row layout
        self._attr_panel = QGroupBox(t("attr.range_title"))
        self._attr_panel.setObjectName("attrPanel")
        attr_layout = QGridLayout(self._attr_panel)
        attr_layout.setSpacing(6)
        attr_layout.setContentsMargins(10, 8, 10, 8)
        for i, attr in enumerate(_ATTR_ORDER):
            name_lbl = QLabel(t(_ATTR_I18N[attr]))
            name_lbl.setObjectName("attrLabel")
            name_lbl.setAlignment(Qt.AlignCenter)
            attr_layout.addWidget(name_lbl, 0, i)
            val_lbl = QLabel("—")
            val_lbl.setObjectName("attrValues")
            val_lbl.setAlignment(Qt.AlignCenter)
            attr_layout.addWidget(val_lbl, 1, i)
            self._attr_bars[attr] = (name_lbl, val_lbl)
        self._attr_est_label = QLabel("")
        self._attr_est_label.setObjectName("attrEstimateLabel")
        self._attr_est_label.setVisible(False)
        attr_layout.addWidget(self._attr_est_label, 2, 0, 1, len(_ATTR_ORDER))
        self._attr_miss_label = QLabel("")
        self._attr_miss_label.setObjectName("attrEstimateLabel")
        self._attr_miss_label.setVisible(False)
        attr_layout.addWidget(self._attr_miss_label, 3, 0, 1, len(_ATTR_ORDER))
        self._attr_panel.setVisible(False)
        rv.addWidget(self._attr_panel)

        # table
        top = QWidget()
        tv = QVBoxLayout(top)
        tv.setContentsMargins(0,0,0,0)
        self._table_caption = QLabel(t("forward.table_caption"))
        self._table_caption.setStyleSheet("font-size:12px;color:#6B6359;padding:2px 6px;")
        tv.addWidget(self._table_caption)

        self.result_table = QTableWidget(0,5)
        self._forward_headers = [
            t("forward.h_icon"), t("forward.h_group"),
            t("forward.h_category"), t("forward.h_probability"),
            t("forward.h_bar"),
        ]
        self.result_table.setHorizontalHeaderLabels(self._forward_headers)
        self.result_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Fixed)
        self.result_table.horizontalHeader().resizeSection(0,50)
        self.result_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(4,QHeaderView.Stretch)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.result_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.result_table.itemClicked.connect(self._on_table_click)
        tv.addWidget(self.result_table)

        # Export button row
        export_row = QHBoxLayout()
        export_row.addStretch()
        self.copy_btn = QPushButton(t("forward.copy_btn"))
        self.copy_btn.setStyleSheet(
            "QPushButton { padding: 4px 16px; border: 1px solid #BBB; "
            "border-radius: 4px; font-size: 12px; }"
            "QPushButton:hover { background: #E8E4DC; }")
        self.copy_btn.clicked.connect(self._copy_as_text)
        export_row.addWidget(self.copy_btn)
        self.export_btn = QPushButton(t("forward.export_btn"))
        self.export_btn.setStyleSheet(
            "QPushButton { padding: 4px 16px; border: 1px solid #BBB; "
            "border-radius: 4px; font-size: 12px; }"
            "QPushButton:hover { background: #E8E4DC; }")
        self.export_btn.clicked.connect(self._export_csv)
        export_row.addWidget(self.export_btn)
        tv.addLayout(export_row)
        self.inner_splitter.addWidget(top)

        # skill tree
        self.skill_tree = SkillTreeWidget(icon_provider=self.icon_provider)
        self.inner_splitter.addWidget(self.skill_tree)
        self.inner_splitter.setSizes([300,400])
        rv.addWidget(self.inner_splitter,1)

        splitter.addWidget(right)
        splitter.setSizes([330,850])
        root.addWidget(splitter,1)

    # ---- data ready ----

    def on_data_ready(self, gd, engine, icon_provider):
        self.gd = gd
        self.engine = engine
        self.icon_provider = icon_provider
        self.skill_tree._icon_provider = icon_provider

        # bg combo
        self.bg_combo.clear()
        filtered = gd.filtered_complete_backgrounds()
        bg_names = []
        for bg_id in filtered:
            zh = gd.bg_name(bg_id)
            self.bg_combo.addItem(zh, bg_id)
            bg_names.append(zh)
        self._bg_model.setStringList(bg_names)
        if filtered:
            self.bg_combo.setCurrentIndex(0)

        # traits
        self._build_trait_grid()

        # sync skill tree language, refresh tooltip if results exist
        self.skill_tree.set_lang(getattr(gd, "lang", "zh"))
        if self._last_results:
            self._fill_skill_tree(self._last_results)

        self.retranslate()

    def retranslate(self):
        """Refresh all static text to current language."""
        self._bg_grp.setTitle(t("forward.char_config"))
        self._bg_label.setText(t("forward.bg_label"))
        self.bg_combo.lineEdit().setPlaceholderText(t("forward.bg_search_ph"))
        self._trait_label.setText(t("forward.traits_label"))
        self._adv_grp.setTitle(t("forward.advanced"))
        self.attr_check.setText(t("forward.use_attr"))
        self.proj_check.setText(t("forward.use_proj"))
        self._mode_label.setText(t("common.mode_label"))
        # mode combo items
        self.mode_combo.setItemText(0, t("mode.analytic"))
        self.mode_combo.setItemText(1, t("mode.monte"))
        self.calc_btn.setText(t("forward.calc_btn"))
        self.trait_search.setPlaceholderText(t("forward.trait_search_ph"))
        self.copy_btn.setText(t("forward.copy_btn"))
        self.export_btn.setText(t("forward.export_btn"))
        self._none_title_lbl.setText(t("forward.none_title"))
        self._table_caption.setText(t("forward.table_caption"))
        # result title: keep placeholder or recompute
        if self._last_results is None:
            self.result_title.setText(t("forward.result_title_ph"))
        else:
            self._refresh_result_title()
        # table headers
        self._forward_headers = [
            t("forward.h_icon"), t("forward.h_group"),
            t("forward.h_category"), t("forward.h_probability"),
            t("forward.h_bar"),
        ]
        self.result_table.setHorizontalHeaderLabels(self._forward_headers)
        # re-fill table if results exist
        if self._last_results is not None:
            self._fill_table(self._last_results)
        # v0.3.0: refresh attribute panel and star control labels
        self._attr_panel.setTitle(t("attr.range_title"))
        for attr, (name_lbl, val_lbl) in self._attr_bars.items():
            name_lbl.setText(t(_ATTR_I18N[attr]))
        for attr, combo in self._star_combos.items():
            for s in range(4):
                combo.setItemText(s, t(f"star.{s}"))
        for attr, lbl in self._star_labels.items():
            lbl.setText(t(_ATTR_I18N[attr]))
        # refresh attribute panel with current bg
        bg_id = self.bg_combo.currentData()
        if bg_id:
            self._refresh_attr_panel(bg_id)

    def _refresh_result_title(self):
        """Rebuild result title from _last_results using current language."""
        if self.gd is None or self._last_results is None:
            return
        trait_ids = [cb.property("trait_id") for cb in self._trait_checkboxes if cb.isChecked()]
        traits_str = ", ".join(self.gd.trait_name(t) for t in trait_ids) if trait_ids else ""
        bg_id = self.bg_combo.currentData()
        if bg_id:
            self.result_title.setText(
                t("forward.result_ok_prefix") + self.gd.bg_name(bg_id) +
                (" + " + traits_str if traits_str else ""))

    def _build_trait_grid(self):
        # clear old
        for cb in self._trait_checkboxes:
            self.trait_grid.removeWidget(cb)
            cb.deleteLater()
        self._trait_checkboxes.clear()

        traits = sorted(self.gd.traits.keys(), key=lambda t: self.gd.trait_name(t))
        for i, tid in enumerate(traits):
            name = self.gd.trait_name(tid)
            cb = QCheckBox(name)
            cb.setObjectName("trait_badge")
            cb.setProperty("trait_id", tid)
            cb.setToolTip(tid)
            cb.toggled.connect(self._on_trait_toggle)
            self._trait_checkboxes.append(cb)
            r, c = divmod(i, self.TRAIT_COLS)
            self.trait_grid.addWidget(cb, r, c)

    def _on_trait_toggle(self, _checked):
        selected = [cb for cb in self._trait_checkboxes if cb.isChecked()]
        if len(selected) > 3:
            sender = self.sender()
            if sender and sender.isChecked():
                sender.blockSignals(True)
                sender.setChecked(False)
                sender.blockSignals(False)
                QMessageBox.warning(self, t("forward.trait_limit_title"),
                                    t("forward.trait_limit_body"))

    # ---- v0.3.0: Attribute range panel ----

    def _on_bg_changed(self, _index):
        """Background selection changed — refresh attribute panel and star controls."""
        bg_id = self.bg_combo.currentData()
        if bg_id and self.gd is not None:
            self._sync_stars_from_engine(bg_id)
            self._refresh_attr_panel(bg_id)

    def _refresh_attr_panel(self, bg_id: str | None):
        """Update the attribute range panel for the given background."""
        if self.gd is None or bg_id is None:
            self._attr_panel.setVisible(False)
            return

        attrs = self.gd.bg_attributes(bg_id)
        is_estimated = self.gd.bg_attribute_estimated(bg_id)
        is_missing = self.gd.bg_attribute_missing(bg_id)

        self._attr_est_label.setVisible(is_estimated)
        self._attr_miss_label.setVisible(is_missing)

        if is_estimated:
            self._attr_est_label.setText("⚠ " + t("attr.estimated"))

        if is_missing:
            self._attr_miss_label.setText("⚠ " + t("attr.missing"))
            for attr in _ATTR_ORDER:
                _, val_lbl = self._attr_bars[attr]
                val_lbl.setText("—")
            self._attr_panel.setVisible(True)
            return

        if not attrs:
            self._attr_panel.setVisible(False)
            return

        for attr in _ATTR_ORDER:
            _, val_lbl = self._attr_bars[attr]
            if attr in attrs:
                mn, mx = attrs[attr]
                val_lbl.setText(f"{mn} – {mx}")
            else:
                val_lbl.setText("—")

        self._attr_panel.setVisible(True)

    # ---- v0.3.0: Star adjustment ----

    def _on_attr_toggled(self, checked):
        """Disable star controls when attribute weighting is off."""
        for combo in self._star_combos.values():
            combo.setEnabled(checked)

    def _on_star_changed(self, _index):
        """Called when any star QComboBox changes. Auto-recalculate."""
        if self._gathering_stars:
            return
        # Auto-recalculate if we have results already
        if self._last_results is not None:
            self._on_calculate()

    def _gather_talent_stars(self) -> dict[str, float]:
        """Collect current star values from UI combos."""
        return {attr: float(combo.currentData())
                for attr, combo in self._star_combos.items()}

    def _sync_stars_from_engine(self, bg_id: str):
        """Set star combos to engine-derived defaults for the given background."""
        if self.engine is None:
            return
        expected = self.engine._bg_expected_talent_stars(bg_id)
        self._gathering_stars = True
        try:
            for attr, combo in self._star_combos.items():
                stars = expected.get(attr, 1.0)
                idx = max(0, min(3, int(round(stars))))
                combo.setCurrentIndex(idx)
        finally:
            self._gathering_stars = False

    # ---- calculate ----

    def _on_calculate(self):
        if self.gd is None or self.engine is None:
            return
        bg_id = self.bg_combo.currentData()
        if not bg_id:
            return
        trait_ids = [cb.property("trait_id") for cb in self._trait_checkboxes if cb.isChecked()]
        use_attr = self.attr_check.isChecked()
        use_proj = self.proj_check.isChecked()
        mode = self.mode_combo.currentData()

        # v0.3.0: Gather talent stars from UI
        talent_stars = self._gather_talent_stars()

        # v0.3.0: Refresh attribute panel
        self._refresh_attr_panel(bg_id)

        try:
            if mode == "monte_carlo":
                res = self.engine.forward_simulate(
                    bg_id, trait_ids, mode="monte_carlo",
                    use_attribute=use_attr, use_projected=use_proj,
                    samples=20000, talent_stars=talent_stars)
            else:
                res = self.engine.forward_simulate(
                    bg_id, trait_ids, mode="analytic",
                    use_attribute=use_attr, use_projected=use_proj,
                    talent_stars=talent_stars)
        except Exception as e:
            QMessageBox.critical(self, t("forward.calc_err_title"),
                                 t("forward.calc_err_prefix") + str(e))
            return

        self._last_results = res
        self.none_label.setVisible(False)
        self.inner_splitter.setVisible(True)

        if res is None:
            self.result_table.setRowCount(0)
            self.result_title.setText(t("forward.result_none"))
            reason = self.engine.forward_reason_if_none(bg_id, trait_ids)
            self.none_reason.setText(reason)
            self.none_label.setVisible(True)
            self.inner_splitter.setVisible(False)
            self.skill_tree.clear()
            return

        traits_str = ", ".join(self.gd.trait_name(t) for t in trait_ids) if trait_ids else ""
        self.result_title.setText(
            t("forward.result_ok_prefix") + self.gd.bg_name(bg_id) +
            (" + " + traits_str if traits_str else ""))
        self._fill_table(res)
        self._fill_skill_tree(res)

    def _fill_table(self, results):
        self.result_table.setRowCount(len(results))
        df = QFont("Consolas", 11)
        df.setStyleHint(QFont.Monospace)

        for row, (group, p) in enumerate(results.items()):
            # icon
            ic = QTableWidgetItem()
            if self.icon_provider:
                ic.setIcon(self.icon_provider.get_icon(group, "groups", 32))
            ic.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 0, ic)
            # name
            ni = QTableWidgetItem(self.gd.group_name(group))
            ni.setData(Qt.UserRole, group)
            self.result_table.setItem(row, 1, ni)
            # category tag
            cat = self.gd.group_category(group) or ""
            cz = cat_name(cat) if cat else cat
            bgc, txc = CAT_COLOR.get(cat, ("#4A4A4A","#FFFFFF"))
            ci = QTableWidgetItem(" " + cz + " ")
            ci.setTextAlignment(Qt.AlignCenter)
            ci.setBackground(QBrush(QColor(bgc)))
            ci.setForeground(QBrush(QColor(txc)))
            ci.setFont(QFont("Microsoft YaHei",10,QFont.Bold))
            self.result_table.setItem(row, 2, ci)
            # prob
            lbl, color = prob_tier_label(p)
            pi = QTableWidgetItem(str(int(p*100))+"% ("+lbl+")")
            pi.setFont(df)
            pi.setForeground(QBrush(QColor(color)))
            pi.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 3, pi)
            # bar
            bar = QProgressBar()
            bar.setRange(0,100)
            bar.setValue(int(p*100))
            bar.setFormat("")
            bar.setTextVisible(False)
            bar.setStyleSheet(
                "QProgressBar::chunk{background:"+color+";border-radius:2px;}"
                "QProgressBar{background:#F0EDE6;border:1px solid #DDD6CC;"
                "border-radius:3px;min-height:14px;max-height:18px;}")
            self.result_table.setCellWidget(row, 4, bar)
            self.result_table.setRowHeight(row, 38)

    def _fill_skill_tree(self, results):
        trees = build_skill_tree_data(self.gd, results)
        if trees is None:
            self.skill_tree.clear()
        else:
            bg_id = self.bg_combo.currentData()
            self.skill_tree.set_trees(trees, bg_id=bg_id, gd=self.gd)

    def _on_table_click(self, item):
        row = item.row()
        ni = self.result_table.item(row, 1)
        if ni is None:
            return
        gid = ni.data(Qt.UserRole)
        if gid:
            self.skill_tree.scroll_to_group(gid)

    def _on_trait_search(self, text):
        """Filter trait checkboxes by search text."""
        q = text.strip().lower()
        for cb in self._trait_checkboxes:
            cb.setVisible(q in cb.text().lower() if q else True)

    # --- export ---

    def _rows_data(self):
        """Yield (group_id, display_name, category, prob) for each non-empty row."""
        for row in range(self.result_table.rowCount()):
            ni = self.result_table.item(row, 1)
            if ni is None:
                continue
            gid = ni.data(Qt.UserRole) or ""
            name = ni.text()
            ci = self.result_table.item(row, 2)
            cat = ci.text().strip() if ci else ""
            pi = self.result_table.item(row, 3)
            prob_text = pi.text() if pi else "0%"
            yield gid, name, cat, prob_text

    def _copy_as_text(self):
        """Copy current table as TSV to clipboard."""
        lines = ["Group ID\tDisplay Name\tCategory\tProbability"]
        for gid, name, cat, prob_text in self._rows_data():
            lines.append(f"{gid}\t{name}\t{cat}\t{prob_text}")
        QApplication.clipboard().setText("\n".join(lines))

    def _export_csv(self):
        """Save current table as CSV file."""
        if self.gd is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, t("forward.export_title"), "forward_results.csv",
            "CSV (*.csv);;All Files (*)")
        if not path:
            return
        import csv
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Group ID", "Display Name", "Category", "Probability"])
            for gid, name, cat, prob_text in self._rows_data():
                w.writerow([gid, name, cat, prob_text])

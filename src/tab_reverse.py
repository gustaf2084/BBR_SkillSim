# -*- coding: utf-8 -*-
"""
tab_reverse.py
反向推导页：选择目标技能树组（可多选），找出最佳背景+特性组合。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QFont, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem,
    QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QGroupBox, QSpinBox, QMessageBox, QSplitter, QDoubleSpinBox, QComboBox,
    QScrollArea, QFrame, QGridLayout, QDialog, QDialogButtonBox,
)

# 类别配置
CAT_ORDER = ["Shared", "Exclusive", "Weapon", "Armor", "Fighting Style", "Special"]
CAT_ZH = {
    "Shared": "共有组",
    "Exclusive": "专属组",
    "Weapon": "武器组",
    "Armor": "护甲组",
    "Fighting Style": "战斗风格",
    "Special": "特殊组",
}
CAT_COLOR = {
    "Shared":        "#27704B",
    "Exclusive":     "#8B6914",
    "Weapon":        "#5A6B7D",
    "Armor":         "#7B6B5A",
    "Fighting Style":"#8B1A6B",
    "Special":       "#B8860B",
}


class ReverseTab(QWidget):
    """反向推导页面。"""

    def __init__(self):
        super().__init__()
        self.gd = None
        self.engine = None
        self.icon_provider = None
        self._cat_panels = {}   # category -> QGroupBox
        self._cat_checkboxes = {}  # category -> list of (QCheckBox, group_id)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # ===== 左侧：目标选择 =====
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setSpacing(8)

        # 目标组选择区（滚动）
        target_grp = QGroupBox("目标技能树组（可多选）")
        target_lv = QVBoxLayout(target_grp)
        target_scroll = QScrollArea()
        target_scroll.setWidgetResizable(True)
        target_scroll.setFrameShape(QFrame.NoFrame)
        self._cat_container = QWidget()
        self._cat_layout = QVBoxLayout(self._cat_container)
        self._cat_layout.setSpacing(4)
        self._cat_layout.setContentsMargins(0, 0, 0, 0)
        target_scroll.setWidget(self._cat_container)
        target_lv.addWidget(target_scroll)
        lv.addWidget(target_grp, 1)

        # 高级选项
        adv_group = QGroupBox("高级选项")
        adv_group.setCheckable(True)
        adv_group.setChecked(False)
        adv_form = QFormLayout(adv_group)

        self.multi_trait_check = QCheckBox("允许多特性组合（最多2个，较慢）")
        adv_form.addRow(self.multi_trait_check)

        self.topn_spin = QSpinBox()
        self.topn_spin.setRange(1, 200)
        self.topn_spin.setValue(20)
        adv_form.addRow("返回数量:", self.topn_spin)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("快速（解析近似）", "analytic")
        self.mode_combo.addItem("精确（蒙特卡洛，较慢）", "monte_carlo")
        adv_form.addRow("计算模式:", self.mode_combo)

        lv.addWidget(adv_group)

        # 推导按钮
        self.derive_btn = QPushButton("◈  推导最佳组合")
        self.derive_btn.setObjectName("primary_btn")
        self.derive_btn.clicked.connect(self._on_derive)
        lv.addWidget(self.derive_btn)

        splitter.addWidget(left)

        # ===== 右侧：结果 =====
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)

        self.result_title = QLabel("选择目标技能树组，点击「推导最佳组合」")
        self.result_title.setObjectName("page_title")
        rv.addWidget(self.result_title)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-size: 13px; color: #6B6359; padding: 4px;")
        self.summary_label.setWordWrap(True)
        rv.addWidget(self.summary_label)

        self.result_table = QTableWidget(0, 4)
        self.result_table.setHorizontalHeaderLabels(["背景", "特性", "概率/得分", "次要组干扰"])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.itemDoubleClicked.connect(self._on_row_double_clicked)
        rv.addWidget(self.result_table, 1)

        # 空结果提示
        self.empty_label = QWidget()
        self.empty_label.setObjectName("notice_parchment")
        elv = QVBoxLayout(self.empty_label)
        el_title = QLabel("⚠ 无可用组合")
        el_title.setObjectName("notice_parchment_title")
        elv.addWidget(el_title)
        el_reason = QLabel("该目标组无任何背景+特性组合可生成。\n尝试选择更通用的组作为目标，或打开高级选项允许多特性组合。")
        el_reason.setWordWrap(True)
        el_reason.setStyleSheet("font-size: 14px; color: #1C1814; padding-top: 4px;")
        elv.addWidget(el_reason)
        self.empty_label.setVisible(False)
        rv.addWidget(self.empty_label)

        splitter.addWidget(right)
        splitter.setSizes([340, 840])
        root.addWidget(splitter, 1)

    # ── 数据就绪 ──────────────────────────────────────────────

    def on_data_ready(self, gd, engine, icon_provider):
        self.gd = gd
        self.engine = engine
        self.icon_provider = icon_provider
        self._build_category_panels()

    def _build_category_panels(self):
        """构建 6 类别折叠面板，每面板内含 QCheckBox 网格。"""
        # 清旧
        for cat, panel in self._cat_panels.items():
            self._cat_layout.removeWidget(panel)
            panel.deleteLater()
        self._cat_panels.clear()
        self._cat_checkboxes.clear()

        for cat in CAT_ORDER:
            groups = self.gd.groups_by_category(cat)
            if not groups:
                continue
            panel = QGroupBox(f"{CAT_ZH.get(cat, cat)} ({len(groups)})")
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
                row, col = divmod(i, 2)  # 2列
                grid.addWidget(cb, row, col)

            self._cat_checkboxes[cat] = cbs
            self._cat_panels[cat] = panel
            self._cat_layout.addWidget(panel)
        self._cat_layout.addStretch()

    # ── 推导 ──────────────────────────────────────────────────

    def _on_derive(self):
        if self.gd is None or self.engine is None:
            return

        # 收集所有已勾选的目标组
        targets = []
        for cat, cbs in self._cat_checkboxes.items():
            for cb, gid in cbs:
                if cb.isChecked():
                    targets.append(gid)

        if not targets:
            QMessageBox.warning(self, "提示", "请至少选择一个目标技能树组。")
            return

        multi_trait = self.multi_trait_check.isChecked()
        top_n = self.topn_spin.value()
        mode = self.mode_combo.currentData()

        try:
            rd = self.engine.reverse_derive(
                targets, mode=mode, multi_trait=multi_trait, max_traits=2,
                top_n=top_n, tiebreak_limit=20)
        except Exception as e:
            QMessageBox.critical(self, "推导错误", f"推导过程出错：\n{e}")
            return

        self.empty_label.setVisible(False)
        self.result_table.setVisible(True)

        if not rd["results"]:
            self.result_table.setRowCount(0)
            self.result_title.setText("反向推导结果：无可用组合")
            self.empty_label.setVisible(True)
            self.summary_label.setText("")
            return

        multi = len(targets) > 1
        title = f"反向推导：{' / '.join(self.gd.group_name(t) for t in targets)}"
        if len(title) > 80:
            title = title[:77] + "..."
        self.result_title.setText(title)

        tiebreak = rd.get("tiebreak_used", False)
        summary_parts = [
            f"最大概率/得分：<b>{rd['max_score']:.4f}</b>",
            f"并列组合：{rd['tied_count']} 个",
            f"返回：{len(rd['results'])} 个",
        ]
        if tiebreak:
            summary_parts.append("（已按次要组干扰排序，干扰越小越纯粹）")
        self.summary_label.setText("　".join(summary_parts))
        self._fill_table(rd["results"], multi)

    def _fill_table(self, results, multi):
        self.result_table.setRowCount(len(results))
        data_font = QFont("Consolas", 11)
        data_font.setStyleHint(QFont.Monospace)

        for row, (bg, traits, score, probs, purity) in enumerate(results):
            # 背景列：图标 + 中文名
            bg_text = self.gd.bg_name(bg)
            bg_item = QTableWidgetItem(f"  {bg_text}  ({bg})")
            if self.icon_provider:
                bg_item.setIcon(self.icon_provider.get_icon(bg, "backgrounds", 24))
            self.result_table.setItem(row, 0, bg_item)

            # 特性列
            trait_text = ", ".join(self.gd.trait_name(t) for t in traits) if traits else "（无）"
            self.result_table.setItem(row, 1, QTableWidgetItem(trait_text))

            # 概率/得分列
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

            # 纯度列（带色标）
            purity_item = QTableWidgetItem(f"{purity:.2f}")
            purity_item.setTextAlignment(Qt.AlignCenter)
            if purity <= 0.5:
                purity_item.setBackground(QBrush(QColor("#E0F0E0")))
                purity_item.setToolTip("非常纯粹，目标组是唯一高概率组")
            elif purity > 2.0:
                purity_item.setBackground(QBrush(QColor("#F0E0E0")))
                purity_item.setToolTip("干扰严重，多个非目标组也有较高概率")
            self.result_table.setItem(row, 3, purity_item)

            self.result_table.setRowHeight(row, 36)

    def _on_row_double_clicked(self, item):
        """双击行 → 弹窗显示该组合的正向模拟详细分布。"""
        row = item.row()
        bg_item = self.result_table.item(row, 0)
        trait_item = self.result_table.item(row, 1)
        if not bg_item or not trait_item:
            return

        # 从背景文本提取 bg_id
        bg_text = bg_item.text().strip()
        # 格式："  中文名  (bg_id)"
        if "(" in bg_text and bg_text.endswith(")"):
            bg_id = bg_text[bg_text.rindex("(") + 1:-1]
        else:
            return

        trait_text = trait_item.text().strip()
        trait_ids = []
        if trait_text != "（无）":
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
            QMessageBox.information(self, "无可用方案", "该组合无可用方案。")
            return

        # 弹窗
        dlg = QDialog(self)
        dlg.setWindowTitle(f"详细概率分布 — {self.gd.bg_name(bg_id)}")
        dlg.resize(550, 500)
        dlv = QVBoxLayout(dlg)

        info = QLabel(f"背景：{self.gd.bg_name(bg_id)}\n"
                      f"特性：{', '.join(self.gd.trait_name(t) for t in trait_ids) if trait_ids else '（无）'}")
        info.setStyleSheet("font-size: 14px; font-weight: bold; padding: 8px;")
        dlv.addWidget(info)

        tbl = QTableWidget(0, 3)
        tbl.setHorizontalHeaderLabels(["技能树组", "类别", "出现概率"])
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
            tbl.setItem(i, 1, QTableWidgetItem(CAT_ZH.get(cat, cat)))
            label_text, color, _ = self._prob_label(p)
            prob_item = QTableWidgetItem(f"{p*100:.1f}%  ({label_text})")
            prob_item.setForeground(QBrush(QColor(color)))
            prob_item.setTextAlignment(Qt.AlignCenter)
            tbl.setItem(i, 2, prob_item)

        dlv.addWidget(tbl, 1)

        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dlg.accept)
        dlv.addWidget(btns)

        dlg.exec()

    @staticmethod
    def _prob_label(p):
        if p >= 0.80:
            return "大概率", "#27704B", "gold"
        if p >= 0.50:
            return "较可能", "#A0522D", "copper"
        if p >= 0.20:
            return "看运气", "#5A6B7D", "iron"
        if p > 0:
            return "小概率", "#8B8378", "gray"
        return "不出现", "#B0B0B0", "dark"

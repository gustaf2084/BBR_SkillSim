# -*- coding: utf-8 -*-
"""
tab_forward.py
正向模拟页：选择背景+特性，展示所有技能树组出现概率分布 + 技能树矩阵可视化。
"""

from collections import OrderedDict

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, QListWidget,
    QListWidgetItem, QCheckBox, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QHeaderView, QGroupBox, QProgressBar, QMessageBox, QSplitter,
    QAbstractItemView,
)

from skill_tree_widget import SkillTreeWidget


# 概率语义标注
def prob_label(p):
    if p >= 0.80:
        return "大概率", "#1e8449"
    if p >= 0.50:
        return "较可能", "#27ae60"
    if p >= 0.20:
        return "看运气", "#d68910"
    if p > 0:
        return "小概率", "#cb4155"
    return "不出现", "#7f8c8d"


class ForwardTab(QWidget):
    """正向模拟页面。"""

    def __init__(self):
        super().__init__()
        self.gd = None
        self.engine = None
        self.icon_provider = None
        self._last_results = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # ===== 左侧：输入区 =====
        left = QWidget()
        lv = QVBoxLayout(left)

        bg_group = QGroupBox("角色配置")
        form = QFormLayout()
        self.bg_combo = QComboBox()
        self.bg_combo.setEditable(False)
        form.addRow("背景:", self.bg_combo)

        self.trait_list = QListWidget()
        self.trait_list.setSelectionMode(QListWidget.MultiSelection)
        self.trait_list.setMaximumHeight(220)
        form.addRow("特性 (可多选):", self.trait_list)

        self.attr_check = QCheckBox("计入天赋星修正")
        self.attr_check.setChecked(True)
        self.proj_check = QCheckBox("计入投影属性修正")
        self.proj_check.setChecked(True)
        form.addRow("", self.attr_check)
        form.addRow("", self.proj_check)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("快速（解析近似）", "analytic")
        self.mode_combo.addItem("精确（蒙特卡洛）", "monte_carlo")
        form.addRow("计算模式:", self.mode_combo)

        bg_group.setLayout(form)
        lv.addWidget(bg_group)

        self.calc_btn = QPushButton("▶  计算概率分布")
        self.calc_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        self.calc_btn.clicked.connect(self._on_calculate)
        lv.addWidget(self.calc_btn)

        lv.addStretch()
        splitter.addWidget(left)

        # ===== 右侧：结果区（上下拆分） =====
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)

        self.result_title = QLabel("请在左侧选择背景与特性，点击「计算概率分布」")
        self.result_title.setStyleSheet("font-size: 15px; font-weight: bold; padding: 6px;")
        rv.addWidget(self.result_title)

        self.none_label = QLabel("⚠ 无可用方案\n\n所选背景与特性组合无法生成任何技能树组。\n请尝试更换特性或背景。")
        self.none_label.setStyleSheet(
            "font-size: 16px; color: #c0392b; background: #fadbd8; "
            "padding: 30px; border: 2px solid #c0392b; border-radius: 8px;")
        self.none_label.setAlignment(Qt.AlignCenter)
        self.none_label.setVisible(False)
        rv.addWidget(self.none_label)

        self.inner_splitter = QSplitter(Qt.Vertical)
        self.inner_splitter.setVisible(False)

        # 上：概率分布表
        top = QWidget()
        tv = QVBoxLayout(top)
        tv.setContentsMargins(0, 0, 0, 0)
        table_title = QLabel("概率分布表（点击行查看下方技能树）")
        table_title.setStyleSheet("font-size: 12px; color: #777; padding: 2px 6px;")
        tv.addWidget(table_title)

        self.result_table = QTableWidget(0, 5)
        self.result_table.setHorizontalHeaderLabels(["图标", "技能树组", "类别", "出现概率", "概率条"])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.result_table.horizontalHeader().resizeSection(0, 50)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.result_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.result_table.itemClicked.connect(self._on_table_row_clicked)
        tv.addWidget(self.result_table)
        self.inner_splitter.addWidget(top)

        # 下：技能树矩阵
        self.skill_tree = SkillTreeWidget(icon_provider=self.icon_provider)
        self.inner_splitter.addWidget(self.skill_tree)

        self.inner_splitter.setSizes([300, 400])
        rv.addWidget(self.inner_splitter, 1)

        splitter.addWidget(right)
        splitter.setSizes([320, 860])
        root.addWidget(splitter, 1)

    # ------------------------------------------------------------------
    # 数据就绪
    # ------------------------------------------------------------------

    def on_data_ready(self, gd, engine, icon_provider):
        self.gd = gd
        self.engine = engine
        self.icon_provider = icon_provider
        self.skill_tree._icon_provider = icon_provider
        self.bg_combo.clear()
        complete = gd.complete_backgrounds()
        for bg_id in complete:
            self.bg_combo.addItem(gd.bg_name(bg_id), bg_id)
        self.trait_list.clear()
        for tname in sorted(gd.traits.keys()):
            item = QListWidgetItem(gd.trait_name(tname))
            item.setData(Qt.UserRole, tname)
            self.trait_list.addItem(item)
        if complete:
            self.bg_combo.setCurrentIndex(0)

    # ------------------------------------------------------------------
    # 计算
    # ------------------------------------------------------------------

    def _on_calculate(self):
        if self.gd is None or self.engine is None:
            return
        bg_id = self.bg_combo.currentData()
        if not bg_id:
            return
        trait_ids = [it.data(Qt.UserRole) for it in self.trait_list.selectedItems()]
        if len(trait_ids) > 3:
            QMessageBox.warning(self, "提示", "特性最多选择 3 个。")
            return
        use_attr = self.attr_check.isChecked()
        use_proj = self.proj_check.isChecked()
        mode = self.mode_combo.currentData()

        try:
            if mode == "monte_carlo":
                res = self.engine.forward_simulate(
                    bg_id, trait_ids, mode="monte_carlo",
                    use_attribute=use_attr, use_projected=use_proj, samples=20000)
            else:
                res = self.engine.forward_simulate(
                    bg_id, trait_ids, mode="analytic",
                    use_attribute=use_attr, use_projected=use_proj)
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程出错：\n{e}")
            return

        self._last_results = res
        self.none_label.setVisible(False)
        self.inner_splitter.setVisible(True)

        if res is None:
            self.result_table.setRowCount(0)
            self.result_title.setText("正向模拟结果：无可用方案")
            reason = self.engine.forward_reason_if_none(bg_id, trait_ids)
            self.none_label.setText(f"⚠ 无可用方案\n\n{reason}")
            self.none_label.setVisible(True)
            self.inner_splitter.setVisible(False)
            self.skill_tree.clear()
            return

        self.result_title.setText(
            f"正向模拟结果：{self.gd.bg_name(bg_id)}  +  "
            f"{', '.join(self.gd.trait_name(t) for t in trait_ids) if trait_ids else '（无）'}")
        self._fill_table(res)
        self._fill_skill_tree(res)

    def _fill_table(self, results):
        self.result_table.setRowCount(len(results))
        for row, (group, p) in enumerate(results.items()):
            icon_item = QTableWidgetItem()
            if self.icon_provider:
                icon_item.setIcon(self.icon_provider.get_icon(group, "groups", 32))
            icon_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 0, icon_item)
            name_item = QTableWidgetItem(self.gd.group_name(group))
            name_item.setData(Qt.UserRole, group)
            self.result_table.setItem(row, 1, name_item)
            cat = self.gd.group_category(group) or ""
            cat_zh = {
                "Shared": "共有组",
                "Exclusive": "专属组",
                "Weapon": "武器组",
                "Armor": "护甲组",
                "Fighting Style": "战斗风格",
                "Special": "特殊组",
                "Always": "常驻",
            }.get(cat, cat)
            cat_item = QTableWidgetItem(cat_zh)
            cat_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 2, cat_item)
            label, color = prob_label(p)
            prob_item = QTableWidgetItem(f"{p*100:.1f}%  ({label})")
            prob_item.setForeground(QBrush(QColor(color)))
            prob_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 3, prob_item)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(p * 100))
            bar.setFormat("")
            bar.setTextVisible(False)
            bar.setStyleSheet(
                f"QProgressBar::chunk {{ background: {color}; }}"
                "QProgressBar { background: #eee; border: 1px solid #ccc; border-radius: 3px; }")
            self.result_table.setCellWidget(row, 4, bar)
        self.result_table.resizeRowsToContents()

    def _fill_skill_tree(self, results):
        trees = []
        for group, prob in results.items():
            if prob <= 0:
                continue
            if self.gd.group_category(group) == "Always":
                continue
            perk_tiers = self.gd.get_perk_tree(group)
            trees.append({
                "group_id": group,
                "group_name": self.gd.group_name(group),
                "probability": prob,
                "tiers": perk_tiers,
            })
        self.skill_tree.set_trees(trees)

    def _on_table_row_clicked(self, item):
        row = item.row()
        name_item = self.result_table.item(row, 1)
        if name_item is None:
            return
        group_id = name_item.data(Qt.UserRole)
        if group_id:
            self.skill_tree.scroll_to_group(group_id)

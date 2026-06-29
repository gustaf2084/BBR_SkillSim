# -*- coding: utf-8 -*-
"""
tab_builds.py
流派推荐页：展示各背景的推荐加点方案与玩法建议。
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel,
    QGroupBox, QTextEdit, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView,
)

from skill_tree_widget import SkillTreeWidget


class BuildsTab(QWidget):
    """流派推荐页面。"""

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

        # 左：背景列表
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.addWidget(QLabel("选择背景:"))
        self.bg_list = QListWidget()
        self.bg_list.currentItemChanged.connect(self._on_bg_changed)
        lv.addWidget(self.bg_list, 1)
        splitter.addWidget(left)

        # 右：推荐方案展示
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)

        self.title = QLabel("")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 6px;")
        rv.addWidget(self.title)

        # 占位说明（精简，不占过多垂直空间）
        self.placeholder = QLabel(
            "流派推荐方案正在编写中。点击参考表中的行可快速定位技能树组。")
        self.placeholder.setStyleSheet(
            "font-size: 12px; color: #555; background: #fef9e7; padding: 4px 12px; "
            "border: 1px solid #f1c40f; border-radius: 4px;")
        self.placeholder.setAlignment(Qt.AlignLeft)
        rv.addWidget(self.placeholder)

        # 上下分割：参考表 + 技能树矩阵
        self.inner_splitter = QSplitter(Qt.Vertical)

        # 上：高概率组参考表
        ref_box = QGroupBox("高概率技能树组（点击行查看下方技能树）")
        rfv = QVBoxLayout(ref_box)
        self.ref_table = QTableWidget(0, 3)
        self.ref_table.setHorizontalHeaderLabels(["技能树组", "类别", "出现概率"])
        self.ref_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ref_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ref_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ref_table.verticalHeader().setVisible(False)
        self.ref_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ref_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ref_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ref_table.itemClicked.connect(self._on_ref_row_clicked)
        rfv.addWidget(self.ref_table)
        self.inner_splitter.addWidget(ref_box)

        # 下：技能树矩阵
        self.skill_tree = SkillTreeWidget(icon_provider=self.icon_provider)
        self.inner_splitter.addWidget(self.skill_tree)

        # 上方表格高度压小，下方技能树矩阵占大头
        self.inner_splitter.setSizes([120, 500])
        rv.addWidget(self.inner_splitter, 1)

        splitter.addWidget(right)
        splitter.setSizes([280, 900])
        root.addWidget(splitter, 1)

    def on_data_ready(self, gd, engine, icon_provider):
        self.gd = gd
        self.engine = engine
        self.icon_provider = icon_provider
        self.skill_tree._icon_provider = icon_provider
        self.bg_list.clear()
        for bg_id in gd.complete_backgrounds():
            item = QListWidgetItem(gd.bg_name(bg_id))
            item.setData(Qt.UserRole, bg_id)
            self.bg_list.addItem(item)
        if self.bg_list.count() > 0:
            self.bg_list.setCurrentRow(0)

    def _on_bg_changed(self, current, previous):
        if current is None or self.gd is None or self.engine is None:
            return
        bg_id = current.data(Qt.UserRole)
        self.title.setText(f"流派推荐 — {self.gd.bg_name(bg_id)}")

        try:
            res = self.engine.forward_simulate(bg_id, [], mode="analytic")
        except Exception:
            res = None

        self._last_results = res

        cat_zh = {
            "Shared": "共有", "Exclusive": "专属", "Weapon": "武器",
            "Armor": "护甲", "Fighting Style": "风格", "Special": "特殊", "Always": "常驻",
        }

        self.ref_table.setRowCount(0)
        if res:
            top = [(g, p) for g, p in res.items() if p > 0][:10]
            self.ref_table.setRowCount(len(top))
            for i, (g, p) in enumerate(top):
                self.ref_table.setItem(i, 0, QTableWidgetItem(self.gd.group_name(g)))
                cat = self.gd.group_category(g) or ""
                self.ref_table.setItem(i, 1, QTableWidgetItem(cat_zh.get(cat, cat)))
                self.ref_table.setItem(i, 2, QTableWidgetItem(f"{p*100:.1f}%"))

        self._fill_skill_tree(res)

    def _fill_skill_tree(self, results):
        if results is None:
            self.skill_tree.clear()
            return
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

    def _on_ref_row_clicked(self, item):
        row = item.row()
        name_item = self.ref_table.item(row, 0)
        if name_item is None or self._last_results is None:
            return
        display_name = name_item.text()
        for group, prob in self._last_results.items():
            if self.gd.group_name(group) == display_name:
                self.skill_tree.scroll_to_group(group)
                return

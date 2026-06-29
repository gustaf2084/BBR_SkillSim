# -*- coding: utf-8 -*-
"""
tab_reverse.py
反向推导页：选择目标技能树组（可多选），找出最佳背景+特性组合。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem,
    QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QGroupBox, QSpinBox, QMessageBox, QSplitter, QDoubleSpinBox, QComboBox,
)


class ReverseTab(QWidget):
    """反向推导页面。"""

    def __init__(self):
        super().__init__()
        self.gd = None
        self.engine = None
        self.icon_provider = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # ===== 左侧：目标选择 =====
        left = QWidget()
        lv = QVBoxLayout(left)

        grp = QGroupBox("目标技能树组（可多选）")
        form = QFormLayout()

        # 目标组多选列表
        self.target_list = QListWidget()
        self.target_list.setSelectionMode(QListWidget.MultiSelection)
        self.target_list.setMaximumHeight(280)
        form.addRow("目标组:", self.target_list)

        # 多特性开关
        self.multi_trait_check = QCheckBox("允许多特性组合（最多2个，较慢）")
        form.addRow("", self.multi_trait_check)

        # top_n
        self.topn_spin = QSpinBox()
        self.topn_spin.setRange(1, 200)
        self.topn_spin.setValue(20)
        form.addRow("返回数量:", self.topn_spin)

        # 计算模式
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("快速（解析近似）", "analytic")
        self.mode_combo.addItem("精确（蒙特卡洛，较慢）", "monte_carlo")
        form.addRow("计算模式:", self.mode_combo)

        grp.setLayout(form)
        lv.addWidget(grp)

        self.derive_btn = QPushButton("▶  推导最佳组合")
        self.derive_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        self.derive_btn.clicked.connect(self._on_derive)
        lv.addWidget(self.derive_btn)

        lv.addStretch()
        splitter.addWidget(left)

        # ===== 右侧：结果 =====
        right = QWidget()
        rv = QVBoxLayout(right)
        self.result_title = QLabel("选择目标技能树组，点击「推导最佳组合」")
        self.result_title.setStyleSheet("font-size: 15px; font-weight: bold; padding: 6px;")
        rv.addWidget(self.result_title)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-size: 13px; color: #555; padding: 4px;")
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
        rv.addWidget(self.result_table, 1)

        self.empty_label = QLabel("⚠ 该目标组无任何背景+特性组合可生成")
        self.empty_label.setStyleSheet(
            "font-size: 15px; color: #c0392b; background: #fadbd8; padding: 20px; "
            "border: 2px solid #c0392b; border-radius: 8px;")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setVisible(False)
        rv.addWidget(self.empty_label)

        splitter.addWidget(right)
        splitter.setSizes([360, 820])
        root.addWidget(splitter, 1)

    def on_data_ready(self, gd, engine, icon_provider):
        self.gd = gd
        self.engine = engine
        self.icon_provider = icon_provider
        self.target_list.clear()
        # 按类别分组展示目标组（中文）
        cat_zh = {
            "Shared": "共有组", "Exclusive": "专属组",
            "Weapon": "武器组", "Armor": "护甲组",
            "Fighting Style": "战斗风格", "Special": "特殊组",
        }
        for cat in ["Shared", "Exclusive", "Weapon", "Armor", "Fighting Style", "Special"]:
            groups = gd.groups_by_category(cat)
            for g in groups:
                item = QListWidgetItem(f"[{cat_zh.get(cat, cat)}] {gd.group_name(g)}")
                item.setData(Qt.UserRole, g)
                self.target_list.addItem(item)

    def _on_derive(self):
        if self.gd is None or self.engine is None:
            return
        targets = [it.data(Qt.UserRole) for it in self.target_list.selectedItems()]
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
        title = f"反向推导：使 {' / '.join(self.gd.group_name(t) for t in targets)} 出现概率最大的组合"
        self.result_title.setText(title)
        tiebreak = rd.get("tiebreak_used", False)
        summary = (f"最大概率/得分：{rd['max_score']:.4f}    "
                   f"并列组合总数：{rd['tied_count']}    "
                   f"返回：{len(rd['results'])} 个    "
                   f"{'（已按次要组干扰排序，干扰越小越纯粹）' if tiebreak else ''}")
        self.summary_label.setText(summary)
        self._fill_table(rd["results"], multi)

    def _fill_table(self, results, multi):
        self.result_table.setRowCount(len(results))
        for row, (bg, traits, score, probs, purity) in enumerate(results):
            self.result_table.setItem(row, 0, QTableWidgetItem(self.gd.bg_name(bg)))
            trait_text = ", ".join(self.gd.trait_name(t) for t in traits) if traits else "（无）"
            self.result_table.setItem(row, 1, QTableWidgetItem(trait_text))

            if multi:
                prob_str = f"{score:.3f}  (" + ", ".join(f"{self.gd.group_name(k)[:4]}={v*100:.0f}%" for k, v in probs.items()) + ")"
            else:
                g = list(probs.keys())[0]
                prob_str = f"{probs[g]*100:.1f}%"
            prob_item = QTableWidgetItem(prob_str)
            prob_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 2, prob_item)

            purity_item = QTableWidgetItem(f"{purity:.2f}")
            purity_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 3, purity_item)

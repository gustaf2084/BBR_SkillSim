# -*- coding: utf-8 -*-
"""
tab_builds.py
流派推荐页：自动数据分析 + 自定义流派方案（builds/*.txt）。
"""

import os
import sys
import subprocess

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel,
    QGroupBox, QTextEdit, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QPushButton, QFrame, QGridLayout, QScrollArea, QMessageBox,
    QSizePolicy,
)
from PySide6.QtGui import QColor, QBrush, QFont

from skill_tree_widget import SkillTreeWidget
from build_parser import scan_builds, generate_template, create_example_file

# 类别配置
CAT_ZH = {
    "Shared": "共有", "Exclusive": "专属", "Weapon": "武器",
    "Armor": "护甲", "Fighting Style": "风格", "Special": "特殊", "Always": "常驻",
}


def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class BuildsTab(QWidget):
    """流派推荐页面。"""

    def __init__(self):
        super().__init__()
        self.gd = None
        self.engine = None
        self.icon_provider = None
        self._last_results = None
        self._current_bg_id = None
        self._builds_data = []      # list of BuildData
        self._build_tag_btns = []   # QPushButton for each build

        self._build_ui()

    # ── UI 构建 ──────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # ── 左侧：背景列表 ──
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setSpacing(6)

        bg_label = QLabel("选择背景:")
        bg_label.setObjectName("section_title")
        lv.addWidget(bg_label)

        self.bg_list = QListWidget()
        self.bg_list.currentItemChanged.connect(self._on_bg_changed)
        lv.addWidget(self.bg_list, 1)

        splitter.addWidget(left)

        # ── 右侧：内容区 ──
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(8)

        # 标题
        self.title = QLabel("")
        self.title.setObjectName("page_title")
        rv.addWidget(self.title)

        # ── 自定义流派区 ──
        self.custom_section = QWidget()
        self.custom_section.setVisible(False)
        cv = QVBoxLayout(self.custom_section)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(6)

        # 流派标签栏
        tag_bar = QWidget()
        tag_layout = QHBoxLayout(tag_bar)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(4)

        tag_lbl = QLabel("自定义流派：")
        tag_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #6B6359;")
        tag_layout.addWidget(tag_lbl)

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

        # 按钮组
        self.new_btn = QPushButton("+ 新建流派")
        self.new_btn.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 2px 10px; "
            "background: transparent; border: 1px dashed #C8BFA8; border-radius: 12px; }"
            "QPushButton:hover { border-color: #B8860B; color: #B8860B; }")
        self.new_btn.clicked.connect(self._on_new_build)
        tag_layout.addWidget(self.new_btn)

        self.edit_btn = QPushButton("📝 编辑")
        self.edit_btn.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 2px 8px; "
            "background: transparent; border: 1px solid #DDD6CC; border-radius: 4px; }"
            "QPushButton:hover { border-color: #C8BFA8; }")
        self.edit_btn.clicked.connect(self._on_edit_build)
        tag_layout.addWidget(self.edit_btn)

        self.folder_btn = QPushButton("📂")
        self.folder_btn.setToolTip("打开 builds 文件夹")
        self.folder_btn.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 2px 6px; "
            "background: transparent; border: 1px solid #DDD6CC; border-radius: 4px; }"
            "QPushButton:hover { border-color: #C8BFA8; }")
        self.folder_btn.clicked.connect(self._on_open_folder)
        tag_layout.addWidget(self.folder_btn)

        cv.addWidget(tag_bar)

        # 流派详细内容
        self.build_detail = QWidget()
        self.build_detail.setObjectName("card")
        bdv = QVBoxLayout(self.build_detail)
        bdv.setSpacing(8)

        # 推荐特性提示
        self.build_traits_hint = QLabel("")
        self.build_traits_hint.setStyleSheet(
            "font-size: 12px; color: #8B6914; background: #FDF8F0; "
            "padding: 4px 10px; border-radius: 4px; font-weight: bold;")
        self.build_traits_hint.setVisible(False)
        bdv.addWidget(self.build_traits_hint)

        # 10 点技能表
        self.perk_table = QTableWidget(0, 5)
        self.perk_table.setHorizontalHeaderLabels(["#", "技能树组", "层级", "技能名", "出现概率"])
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

        # 玩法建议
        self.playstyle_text = QLabel("")
        self.playstyle_text.setWordWrap(True)
        self.playstyle_text.setStyleSheet(
            "font-size: 12px; color: #1C1814; padding: 8px; "
            "background: #FAFAF6; border-radius: 4px; line-height: 1.6;")
        self.playstyle_text.setVisible(False)
        bdv.addWidget(self.playstyle_text)

        cv.addWidget(self.build_detail)
        rv.addWidget(self.custom_section)

        # ── 自动分析区 ──
        auto_label = QLabel("自动数据分析")
        auto_label.setObjectName("section_title")
        rv.addWidget(auto_label)

        self.auto_cards = QWidget()
        ac_layout = QHBoxLayout(self.auto_cards)
        ac_layout.setSpacing(10)
        ac_layout.setContentsMargins(0, 0, 0, 0)

        # 三张卡片
        self._card_defense = self._make_auto_card("🛡 防御核心")
        self._card_offense = self._make_auto_card("⚔ 攻击方向")
        self._card_special = self._make_auto_card("⭐ 特殊潜力")
        ac_layout.addWidget(self._card_defense, 1)
        ac_layout.addWidget(self._card_offense, 1)
        ac_layout.addWidget(self._card_special, 1)

        rv.addWidget(self.auto_cards)

        # ── 引导提示（无自定义方案时） ──
        self.guide_hint = QLabel(
            "💡 想在 <b>builds/</b> 目录中创建流派方案文件，自定义推荐加点。"
            "点击「+ 新建流派」即可开始。")
        self.guide_hint.setStyleSheet(
            "font-size: 12px; color: #6B6359; padding: 6px 12px; "
            "background: #F5F0E8; border-radius: 4px;")
        self.guide_hint.setVisible(False)
        rv.addWidget(self.guide_hint)

        # ── 技能树矩阵 ──
        self.skill_tree = SkillTreeWidget(icon_provider=self.icon_provider)
        rv.addWidget(self.skill_tree, 1)

        splitter.addWidget(right)
        splitter.setSizes([280, 900])
        root.addWidget(splitter, 1)

    def _make_auto_card(self, title_text):
        card = QFrame()
        card.setObjectName("card")
        clv = QVBoxLayout(card)
        clv.setSpacing(4)
        title = QLabel(title_text)
        title.setObjectName("section_title")
        clv.addWidget(title)
        content = QLabel("选择背景后自动分析")
        content.setWordWrap(True)
        content.setStyleSheet("font-size: 12px; color: #6B6359; line-height: 1.5;")
        content.setMinimumHeight(60)
        clv.addWidget(content, 1)
        card.setProperty("card_content", content)
        return card

    # ── 数据就绪 ──────────────────────────────────────────────

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

    # ── 背景切换 ──────────────────────────────────────────────

    def _on_bg_changed(self, current, previous):
        if current is None or self.gd is None or self.engine is None:
            return
        bg_id = current.data(Qt.UserRole)
        self._current_bg_id = bg_id
        self.title.setText(f"流派推荐 — {self.gd.bg_name(bg_id)}")

        # 正向模拟
        try:
            res = self.engine.forward_simulate(bg_id, [], mode="analytic")
        except Exception:
            res = None
        self._last_results = res

        # 加载该背景的自定义流派
        self._load_builds(bg_id)

        # 刷新自动分析卡片
        self._refresh_auto_cards(res)

        # 刷新技能树
        self._fill_skill_tree(res)

    # ── 自动分析卡片 ──────────────────────────────────────────

    def _refresh_auto_cards(self, results):
        if results is None:
            for card_id in ["defense", "offense", "special"]:
                widget = getattr(self, f"_card_{card_id}", None)
                if widget:
                    lbl = widget.property("card_content")
                    if lbl:
                        lbl.setText("（无可用方案）")
            return

        # 防御核心：护甲 + 盾 + 通用生存
        defense_groups = {"Heavy Armor", "Medium Armor", "Light Armor", "Shield",
                          "Tough", "Unstoppable", "Agile", "Fast", "Trained", "Vigorous"}
        self._fill_card("defense", results, defense_groups)

        # 攻击方向：武器 + 战斗风格
        offense_groups = {"Axe", "Bow", "Cleaver", "Crossbow", "Dagger", "Flail",
                          "Hammer", "Mace", "Polearm", "Spear", "Sword", "Throwing",
                          "Cross", "Whip",
                          "Swift", "Power", "Mighty Blow", "Deft Blow", "Melee Fighting Style",
                          "Ranged", "Ranged Fighting Style", "Shield Fighting Style"}
        self._fill_card("offense", results, offense_groups)

        # 特殊潜力：专属 + 特殊 + 低概率但有价值的
        special_groups = set()
        for g in self.gd.groups:
            cat = self.gd.group_category(g)
            if cat in ("Exclusive", "Special"):
                special_groups.add(g)
        special_groups.update({"Back to Basics", "Tactician"})
        self._fill_card("special", results, special_groups)

    def _fill_card(self, card_id, results, group_set):
        widget = getattr(self, f"_card_{card_id}", None)
        if widget is None:
            return
        lbl = widget.property("card_content")
        if lbl is None:
            return

        relevant = []
        for g, p in results.items():
            if g in group_set and p > 0:
                relevant.append((g, p))
        relevant.sort(key=lambda x: -x[1])
        top10 = relevant[:10]

        if not top10:
            lbl.setText("（无相关组）")
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

    # ── 自定义流派 ────────────────────────────────────────────

    def _get_builds_dir(self):
        return os.path.join(_app_dir(), "builds")

    def _load_builds(self, bg_id):
        """加载匹配当前背景的自定义流派方案。"""
        builds_dir = self._get_builds_dir()

        # 首次启动：创建示例文件
        create_example_file(builds_dir)

        all_builds = scan_builds(builds_dir)
        self._builds_data = [b for b in all_builds
                             if b.background == bg_id and b.is_valid()]

        # 重建标签栏
        self._rebuild_tag_bar()

        if self._builds_data:
            self.custom_section.setVisible(True)
            self.guide_hint.setVisible(False)
            self._select_build(0)
        else:
            self.custom_section.setVisible(False)
            self.guide_hint.setVisible(True)
            self._clear_build_detail()

    def _rebuild_tag_bar(self):
        # 清旧
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
        bd = self._builds_data[idx]

        # 更新标签选中态
        for i, btn in enumerate(self._build_tag_btns):
            btn.setChecked(i == idx)

        self._show_build_detail(bd)

    def _show_build_detail(self, bd):
        """在右侧展示流派详细内容。"""
        # 推荐特性提示
        if bd.traits:
            trait_zh = []
            for tid in bd.traits:
                tname = self.gd.trait_name(tid) if self.gd else tid
                trait_zh.append(tname)
            self.build_traits_hint.setText(f"推荐特性：{', '.join(trait_zh)}")
            self.build_traits_hint.setVisible(True)
        else:
            self.build_traits_hint.setVisible(False)

        # 技能点表
        self.perk_table.setRowCount(len(bd.perks))
        data_font = QFont("Consolas", 11)
        data_font.setStyleHint(QFont.Monospace)

        for row, (order, group, tier, perk_name) in enumerate(bd.perks):
            # 序号
            order_item = QTableWidgetItem(str(order))
            order_item.setTextAlignment(Qt.AlignCenter)
            self.perk_table.setItem(row, 0, order_item)

            # 技能树组
            gname = self.gd.group_name(group) if self.gd else group
            self.perk_table.setItem(row, 1, QTableWidgetItem(gname))

            # 层级
            self.perk_table.setItem(row, 2, QTableWidgetItem(tier))

            # 技能名
            self.perk_table.setItem(row, 3, QTableWidgetItem(perk_name))

            # 该组在当前背景下的出现概率
            prob = 0
            if self._last_results and group in self._last_results:
                prob = self._last_results[group]
            prob_item = QTableWidgetItem(f"{prob*100:.1f}%")
            prob_item.setFont(data_font)
            prob_item.setTextAlignment(Qt.AlignCenter)

            if prob < 0.20 and prob > 0:
                prob_item.setForeground(QBrush(QColor("#C0392B")))
                prob_item.setToolTip(f"⚠ 低概率：建议搭配特性提升 {gname} 组出现概率")
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

        # 解析错误
        if bd.parse_errors:
            err_text = "解析问题：\n" + "\n".join(bd.parse_errors[:5])
            self.playstyle_text.setText(err_text)
            self.playstyle_text.setStyleSheet(
                "font-size: 11px; color: #C0392B; padding: 8px; "
                "background: #FDF0F0; border-radius: 4px;")
            self.playstyle_text.setVisible(True)

    def _clear_build_detail(self):
        self.build_traits_hint.setVisible(False)
        self.perk_table.setRowCount(0)
        self.playstyle_text.setVisible(False)

    # ── 按钮事件 ──────────────────────────────────────────────

    def _on_new_build(self):
        if not self._current_bg_id:
            return
        name = self.gd.bg_name(self._current_bg_id) if self.gd else self._current_bg_id
        builds_dir = self._get_builds_dir()
        filepath = generate_template(self._current_bg_id, name, builds_dir)

        # 尝试用系统编辑器打开
        try:
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", filepath])
            else:
                subprocess.Popen(["xdg-open", filepath])
        except Exception:
            QMessageBox.information(self, "文件已创建",
                                    f"流派文件已创建：\n{filepath}\n请用文本编辑器打开编辑。")

        # 重新加载
        self._load_builds(self._current_bg_id)

    def _on_edit_build(self):
        """编辑当前选中的流派文件。"""
        if not self._builds_data:
            return
        # 找到当前选中的
        for i, btn in enumerate(self._build_tag_btns):
            if btn.isChecked() and i < len(self._builds_data):
                bd = self._builds_data[i]
                filepath = os.path.join(self._get_builds_dir(), bd.filename)
                try:
                    if sys.platform == "win32":
                        os.startfile(filepath)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", filepath])
                    else:
                        subprocess.Popen(["xdg-open", filepath])
                except Exception:
                    QMessageBox.warning(self, "错误", f"无法打开文件：{filepath}")
                return

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
            QMessageBox.warning(self, "错误", f"无法打开文件夹：{builds_dir}")

    # ── 技能树矩阵 ────────────────────────────────────────────

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

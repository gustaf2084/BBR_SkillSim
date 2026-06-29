# -*- coding: utf-8 -*-
"""
tab_about.py
关于页：软件说明、数据版本、使用提示。
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QGroupBox


class AboutTab(QWidget):
    """关于页面。"""

    def __init__(self):
        super().__init__()
        self.gd = None
        self._build_ui()

    def _build_ui(self):
        v = QVBoxLayout(self)

        title = QLabel("战场兄弟·重铸 — 技能树模拟器")
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        info_box = QGroupBox("数据与版本")
        ilv = QVBoxLayout(info_box)
        self.info_label = QLabel("（数据未加载）")
        self.info_label.setStyleSheet("font-size: 14px; padding: 10px;")
        ilv.addWidget(self.info_label)
        v.addWidget(info_box)

        desc_box = QGroupBox("功能说明")
        dlv = QVBoxLayout(desc_box)
        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setHtml(
            "<h3>三大功能</h3>"
            "<p><b>正向模拟</b>：选择角色的背景与特性，计算并展示所有可能生成的技能树组"
            "及其出现概率分布。用于<b>招人前预判</b>能期待什么技能树。</p>"
            "<p><b>反向推导</b>：选择目标技能树组（可多选），找出使其出现概率最大的"
            "背景+特性组合。用于<b>从需求倒推选人</b>——想要某种 build 该招什么人。</p>"
            "<p><b>流派推荐</b>：查看各背景的推荐技能加点方案与玩法建议（编写中）。</p>"
            "<h3>使用提示</h3>"
            "<p>• 概率标注：<b>大概率</b>≥80% / <b>较可能</b>≥50% / <b>看运气</b>≥20% / "
            "<b>小概率</b>&lt;20%。</p>"
            "<p>• 计算模式：快速（解析近似）即时返回；精确（蒙特卡洛）更慢但结果稳定。</p>"
            "<p>• 反向推导多目标时，天然有区分度；单目标且该组对某些背景是 100% 时，"
            "会按「次要组干扰」排序，干扰越小表示该组合越纯粹地服务目标组。</p>"
            "<h3>数据说明</h3>"
            "<p>• 数据源自《战场兄弟·重铸》mod 0.7.6 的角色数据文档（data.json）。</p>"
            "<p>• 「技能树组出现概率」= 给定背景+特性下，该组在最终生成树中至少被骰出一次的概率。</p>"
            "<p>• 本软件为社区工具，与游戏官方及 mod 作者无隶属关系。</p>"
        )
        dlv.addWidget(desc)
        v.addWidget(desc_box, 1)

    def set_info(self, gd):
        self.gd = gd
        if gd is None:
            return
        inc = gd.incomplete_backgrounds()
        info = (
            f"游戏数据版本：{gd.version}<br>"
            f"背景数量：{len(gd.backgrounds)}（可用 {len(gd.complete_backgrounds())}，"
            f"不完整 {len(inc)}）<br>"
            f"特性数量：{len(gd.traits)}<br>"
            f"技能树组：{len(gd.groups)}<br>"
            f"默认等级：{gd.max_level}（{gd.skill_points} 技能点）<br>"
        )
        if inc:
            info += f"<br>数据不完整的背景（已隐藏）：{', '.join(inc)}"
        if gd.warnings:
            info += f"<br><br>数据告警 {len(gd.warnings)} 条（详见日志）。"
        self.info_label.setText(info)

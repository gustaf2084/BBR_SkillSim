# -*- coding: utf-8 -*-
"""
tab_about.py
关于页：软件说明、数据版本、使用提示 — 卡片化布局。
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QGroupBox,
    QFrame, QSizePolicy, QGridLayout,
)


class AboutTab(QWidget):
    """关于页面。"""

    def __init__(self):
        super().__init__()
        self.gd = None
        self._build_ui()

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setSpacing(12)
        v.setContentsMargins(24, 20, 24, 20)

        # 标题
        title = QLabel("战场兄弟·重铸 — 技能树模拟器")
        title.setObjectName("page_title")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        # ── 三列卡片 ──
        cards = QHBoxLayout()
        cards.setSpacing(12)

        # 卡片 1：数据信息
        cards.addWidget(self._build_card("📊 数据信息", "data_info"))

        # 卡片 2：功能说明
        cards.addWidget(self._build_card("⚙ 功能说明", "features"))

        # 卡片 3：使用提示
        cards.addWidget(self._build_card("💡 概率图例", "legend"))

        v.addLayout(cards)

        # 底部说明
        footer = QLabel("")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 11px; color: #A09888; padding: 12px;")
        footer.setWordWrap(True)
        v.addWidget(footer)

    def _build_card(self, title_text, card_id):
        card = QFrame()
        card.setObjectName("card")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        clv = QVBoxLayout(card)
        clv.setSpacing(8)

        title = QLabel(title_text)
        title.setObjectName("section_title")
        clv.addWidget(title)

        content = QLabel("")
        content.setWordWrap(True)
        content.setStyleSheet("font-size: 12px; color: #1C1814; line-height: 1.6;")
        content.setObjectName(f"card_{card_id}")
        clv.addWidget(content, 1)

        setattr(self, f"_card_{card_id}", content)
        return card

    def set_info(self, gd):
        self.gd = gd
        if gd is None:
            return

        inc = gd.incomplete_backgrounds()

        # 卡片 1：数据
        data_text = (
            f"<p>游戏数据版本：<b>{gd.version}</b></p>"
            f"<p>背景数量：<b>{len(gd.backgrounds)}</b>"
            f"（可用 {len(gd.complete_backgrounds())}，不完整 {len(inc)}）</p>"
            f"<p>特性数量：<b>{len(gd.traits)}</b></p>"
            f"<p>技能树组：<b>{len(gd.groups)}</b></p>"
            f"<p>默认等级：{gd.max_level}（{gd.skill_points} 技能点）</p>"
        )
        if inc:
            data_text += f"<p style='font-size:11px; color:#8B8378;'>"
            data_text += f"不完整背景（已隐藏）：{', '.join(inc[:10])}"
            if len(inc) > 10:
                data_text += f" …等 {len(inc)} 个"
            data_text += "</p>"
        if gd.warnings:
            data_text += (
                f"<p style='font-size:11px; color:#A0522D;'>"
                f"数据告警 {len(gd.warnings)} 条（详见日志）</p>"
            )
        self._card_data_info.setText(data_text)

        # 卡片 2：功能
        features_text = (
            "<p><b>正向模拟</b>——选择背景与特性，查看所有可能生成的技能树组"
            "及其出现概率分布。用于招人前预判。</p>"
            "<p><b>反向推导</b>——选择目标技能树组，找出使其出现概率最大的"
            "背景+特性组合。从需求倒推选人。</p>"
            "<p><b>流派推荐</b>——自动分析各背景的技能树倾向，"
            "支持自定义流派方案文件（builds/*.txt）编辑与分享。</p>"
        )
        self._card_features.setText(features_text)

        # 卡片 3：概率图例
        legend_text = (
            "<p style='color:#27704B;'>● <b>大概率 ≥80%</b> — 几乎必然出现</p>"
            "<p style='color:#A0522D;'>● <b>较可能 50–80%</b> — 多数情况出现</p>"
            "<p style='color:#5A6B7D;'>● <b>看运气 20–50%</b> — 有希望但不稳</p>"
            "<p style='color:#8B8378;'>● <b>小概率 &lt;20%</b> — 不推荐依赖</p>"
            "<p style='color:#B0B0B0;'>● <b>不出现 =0</b> — 无法生成</p>"
            "<p style='font-size:11px; color:#8B8378; margin-top:8px;'>"
            "提示：高概率不一定好（你可能不想要该组），低概率不一定坏（出了是惊喜）。</p>"
        )
        self._card_legend.setText(legend_text)

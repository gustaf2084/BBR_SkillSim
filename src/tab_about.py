# -*- coding: utf-8 -*-
"""
tab_about.py
About page — software info, data version, usage tips in card layout.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from i18n import t


class AboutTab(QWidget):
    """About page with retranslate support."""

    def __init__(self):
        super().__init__()
        self.gd = None
        self._build_ui()

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setSpacing(12)
        v.setContentsMargins(24, 20, 24, 20)

        # title
        self._page_title = QLabel(t("about.title"))
        self._page_title.setObjectName("page_title")
        self._page_title.setAlignment(Qt.AlignCenter)
        v.addWidget(self._page_title)

        # ── three card columns ──
        cards = QHBoxLayout()
        cards.setSpacing(12)

        # card 1: data info
        self._card1 = self._build_card(t("about.card_data"), "data_info")
        cards.addWidget(self._card1)

        # card 2: features
        self._card2 = self._build_card(t("about.card_features"), "features")
        cards.addWidget(self._card2)

        # card 3: legend
        self._card3 = self._build_card(t("about.card_legend"), "legend")
        cards.addWidget(self._card3)

        v.addLayout(cards)

        # footer
        self._footer = QLabel("")
        self._footer.setAlignment(Qt.AlignCenter)
        self._footer.setStyleSheet("font-size: 11px; color: #A09888; padding: 12px;")
        self._footer.setWordWrap(True)
        v.addWidget(self._footer)

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
        setattr(self, f"_card_title_{card_id}", title)
        return card

    def set_info(self, gd):
        self.gd = gd
        self._refresh_content()

    def retranslate(self):
        """Refresh all visible text to current language."""
        self._page_title.setText(t("about.title"))
        self._card_title_data_info.setText(t("about.card_data"))
        self._card_title_features.setText(t("about.card_features"))
        self._card_title_legend.setText(t("about.card_legend"))
        self._refresh_content()

    def _refresh_content(self):
        if self.gd is None:
            return
        gd = self.gd
        inc = gd.incomplete_backgrounds()

        # card 1: data
        data_text = (
            f"<p>{t('about.data_version')}<b>{gd.version}</b></p>"
            f"<p>{t('about.data_bg_count')}<b>{len(gd.backgrounds)}</b>"
            f"（{t('about.data_bg_avail')}{len(gd.complete_backgrounds())}，"
            f"{t('about.data_bg_incomplete')}{len(inc)}）</p>"
            f"<p>{t('about.data_trait_count')}<b>{len(gd.traits)}</b></p>"
            f"<p>{t('about.data_group_count')}<b>{len(gd.groups)}</b></p>"
            f"<p>{t('about.data_level')}{gd.max_level}（"
            f"{t('about.data_skill_pts').format(gd.skill_points)}）</p>"
        )
        if inc:
            data_text += "<p style='font-size:11px; color:#8B8378;'>"
            data_text += f"{t('about.data_hidden')}{', '.join(inc[:10])}"
            if len(inc) > 10:
                data_text += f" …{t('about.data_bg_incomplete')}{len(inc)} "
            data_text += "</p>"
        if gd.warnings:
            data_text += (
                f"<p style='font-size:11px; color:#A0522D;'>"
                f"{t('about.data_warnings').format(len(gd.warnings))}</p>"
            )
        self._card_data_info.setText(data_text)

        # card 2: features
        self._card_features.setText(t("about.features_text"))

        # card 3: legend
        self._card_legend.setText(t("about.legend_text"))

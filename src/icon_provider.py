# -*- coding: utf-8 -*-
"""
icon_provider.py
Icon loading with SVG placeholder fallback for nav/UI icons,
and PNG-based perk icon loading from icons/ directory.
"""

import os
import re

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer

# ── Inline SVG icons (theme-aware, 32x32 viewBox) ──────────────────

_NAV_FORWARD_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <path d="M6 16h18M20 8l8 8-8 8" stroke="{color}" stroke-width="2.5" fill="none"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

_NAV_REVERSE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <path d="M26 16H8M12 24l-8-8 8-8" stroke="{color}" stroke-width="2.5" fill="none"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

_NAV_BUILDS_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect x="4" y="4" width="10" height="10" rx="2" stroke="{color}" stroke-width="2" fill="none"/>
  <rect x="18" y="4" width="10" height="10" rx="2" stroke="{color}" stroke-width="2" fill="none"/>
  <rect x="4" y="18" width="10" height="10" rx="2" stroke="{color}" stroke-width="2" fill="none"/>
  <rect x="18" y="18" width="10" height="10" rx="2" stroke="{color}" stroke-width="2" fill="none"/>
</svg>"""

_NAV_ABOUT_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="12" stroke="{color}" stroke-width="2" fill="none"/>
  <text x="16" y="21" text-anchor="middle" font-size="16" font-weight="bold"
        fill="{color}" font-family="sans-serif">i</text>
</svg>"""

_THEME_LIGHT_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="6" stroke="{color}" stroke-width="2" fill="none"/>
  <g stroke="{color}" stroke-width="2" stroke-linecap="round">
    <line x1="16" y1="3" x2="16" y2="7"/>
    <line x1="16" y1="25" x2="16" y2="29"/>
    <line x1="3" y1="16" x2="7" y2="16"/>
    <line x1="25" y1="16" x2="29" y2="16"/>
    <line x1="6.8" y1="6.8" x2="9.6" y2="9.6"/>
    <line x1="22.4" y1="22.4" x2="25.2" y2="25.2"/>
    <line x1="6.8" y1="25.2" x2="9.6" y2="22.4"/>
    <line x1="22.4" y1="9.6" x2="25.2" y2="6.8"/>
  </g>
</svg>"""

_THEME_DARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <path d="M26 18.5A10 10 0 0 1 13.5 6 10 10 0 1 0 26 18.5z"
        stroke="{color}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

_LANG_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="12" stroke="{color}" stroke-width="2" fill="none"/>
  <ellipse cx="16" cy="16" rx="6" ry="12" stroke="{color}" stroke-width="1.5" fill="none"/>
  <line x1="4" y1="12" x2="28" y2="12" stroke="{color}" stroke-width="1.5"/>
  <line x1="4" y1="20" x2="28" y2="20" stroke="{color}" stroke-width="1.5"/>
</svg>"""

_PLACEHOLDER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <polygon points="16,4 28,16 16,28 4,16" stroke="{color}" stroke-width="2"
           fill="none" stroke-linejoin="round"/>
</svg>"""


def _render_svg(svg_template, color_hex, size=32):
    """Render an inline SVG template to a QPixmap."""
    svg_str = svg_template.format(color=color_hex)
    renderer = QSvgRenderer(QByteArray(svg_str.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def make_nav_icon(svg_template, color_hex, size=24):
    """Create a QIcon from an SVG template for navigation use."""
    return QIcon(_render_svg(svg_template, color_hex, size))


PLACEHOLDER_COLORS = {
    "backgrounds": QColor(60, 90, 140),
    "traits": QColor(120, 70, 130),
    "groups": QColor(70, 120, 90),
    "default": QColor(90, 90, 90),
}

# 技能名与素材文件名对不上的显式别名（键/值均为归一化名）。
# 别名优先于同名直查：perk_crossbow_mastery.png 的图案并非弩，
# 正确素材是 Reforged 的 crossbow_and_firearms_mastery。
PERK_ICON_ALIASES = {
    "crossbow_mastery": "crossbow_and_firearms_mastery",
    # 剑圣组素材带 swordmaster_ 前缀，节点名不带
    "blade_dancer": "swordmaster_blade_dancer",
    "juggernaut": "swordmaster_juggernaut",
    "metzger": "swordmaster_metzger",
    "precise": "swordmaster_precise",
    "reaper": "swordmaster_reaper",
    "versatile_swordsman": "swordmaster_versatile_swordsman",
    "kick": "swordmaster_grappler",  # 剑圣第7层（Kick/Push Through/Tackle）
    # Reforged 素材沿用 mod 内部命名
    "mentor_presence": "mentor",
    "return_favor": "retribution",
    "sundering_strikes": "dent_armor",
}


class IconProvider:

    def __init__(self, icons_dir=None, size=32):
        if icons_dir is None:
            here = os.path.dirname(os.path.abspath(__file__))
            try:
                import sys
                if getattr(sys, "frozen", False):
                    here = os.path.dirname(sys.executable)
            except Exception:
                pass
            icons_dir = os.path.join(here, "icons")
        self.icons_dir = icons_dir
        self.size = size
        self._cache = {}
        self._svg_cache = {}
        self._missing = set()
        self._icons_available = os.path.isdir(icons_dir)
        self._perk_icon_map = {}
        if self._icons_available:
            self._build_perk_map()

    # ── SVG nav/UI icons (theme-aware) ───────────────────────────

    NAV_ICONS = {
        "forward": _NAV_FORWARD_SVG,
        "reverse": _NAV_REVERSE_SVG,
        "builds": _NAV_BUILDS_SVG,
        "about": _NAV_ABOUT_SVG,
    }

    def get_nav_icon(self, name, color_hex, size=24):
        cache_key = ("nav", name, color_hex, size)
        if cache_key in self._svg_cache:
            return self._svg_cache[cache_key]
        svg = self.NAV_ICONS.get(name)
        if svg is None:
            return QIcon()
        icon = make_nav_icon(svg, color_hex, size)
        self._svg_cache[cache_key] = icon
        return icon

    def get_theme_icon(self, is_dark, color_hex, size=18):
        cache_key = ("theme", is_dark, color_hex, size)
        if cache_key in self._svg_cache:
            return self._svg_cache[cache_key]
        svg = _THEME_DARK_SVG if is_dark else _THEME_LIGHT_SVG
        icon = make_nav_icon(svg, color_hex, size)
        self._svg_cache[cache_key] = icon
        return icon

    def get_lang_icon(self, color_hex, size=18):
        cache_key = ("lang", color_hex, size)
        if cache_key in self._svg_cache:
            return self._svg_cache[cache_key]
        icon = make_nav_icon(_LANG_SVG, color_hex, size)
        self._svg_cache[cache_key] = icon
        return icon

    def get_placeholder_pixmap(self, color_hex, size=28):
        cache_key = ("placeholder", color_hex, size)
        if cache_key in self._svg_cache:
            return self._svg_cache[cache_key]
        pix = _render_svg(_PLACEHOLDER_SVG, color_hex, size)
        self._svg_cache[cache_key] = pix
        return pix

    @staticmethod
    def _normalize_perk_name(name):
        s = name.lower()
        s = re.sub(r"\s*\(.*?\)\s*", "", s)
        s = re.sub(r"'s?", "", s)
        s = re.sub(r"[^a-z0-9]+", "_", s)
        s = s.strip("_")
        return s

    @staticmethod
    def _normalize_compact(name):
        return name.replace("_", "")

    def _build_perk_map(self):
        self._perk_icon_map = {}
        if not self._icons_available:
            return
        scan_dirs = [
            self.icons_dir,
            os.path.join(self.icons_dir, "perks"),
        ]
        for scan_dir in scan_dirs:
            if not os.path.isdir(scan_dir):
                continue
            for fname in os.listdir(scan_dir):
                if not fname.lower().endswith(".png"):
                    continue
                if fname.endswith("_sw.png"):
                    continue
                if not (fname.startswith("perk_") or fname.startswith("perk_rf_")):
                    continue
                full = os.path.join(scan_dir, fname)
                stem = fname.replace(".png", "")
                for prefix in ("perk_rf_", "perk_"):
                    if stem.startswith(prefix):
                        stem = stem[len(prefix):]
                        break
                norm = self._normalize_perk_name(stem)
                compact = self._normalize_compact(norm)
                if norm:
                    self._perk_icon_map[norm] = full
                    self._perk_icon_map[compact] = full
                if stem != norm:
                    self._perk_icon_map[stem.lower()] = full

    def get_perk_icon(self, perk_en_name, size=None):
        size = size or self.size
        key = ("perk", perk_en_name, size)
        if key in self._cache:
            return self._cache[key]
        pix = None
        norm = self._normalize_perk_name(perk_en_name)
        compact = self._normalize_compact(norm)
        alias = PERK_ICON_ALIASES.get(norm) or PERK_ICON_ALIASES.get(compact)
        candidates = []
        if alias:
            candidates.extend((alias, self._normalize_compact(alias)))
        candidates.extend((norm, compact))
        for candidate in candidates:
            if candidate in self._perk_icon_map:
                pix = QPixmap(self._perk_icon_map[candidate])
                if not pix.isNull():
                    break
        if (pix is None or pix.isNull()) and norm:
            for suffix in ("_effect", "_skill"):
                if norm.endswith(suffix):
                    shorter = norm[:-len(suffix)]
                    shorter_compact = self._normalize_compact(shorter)
                    for c in (shorter, shorter_compact):
                        if c in self._perk_icon_map:
                            pix = QPixmap(self._perk_icon_map[c])
                            if not pix.isNull():
                                break
        if pix is None or pix.isNull():
            self._missing.add(("perk", perk_en_name))
        result = pix if (pix and not pix.isNull()) else QPixmap()
        self._cache[key] = result
        return result

    @property
    def skill_icons_available(self):
        return self._icons_available

    @property
    def icons_available(self):
        return self._icons_available

    def _placeholder(self, subdir, name, size=None):
        sz = size or self.size
        color = PLACEHOLDER_COLORS.get(subdir, PLACEHOLDER_COLORS["default"])
        img = QImage(sz, sz, QImage.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        r = sz // 6
        top_c = color.lighter(115)
        bot_c = color.darker(110)
        grad_path = QPainterPath()
        grad_path.addRoundedRect(0, 0, sz, sz, r, r)
        lg = QLinearGradient(0, 0, 0, sz)
        lg.setColorAt(0, top_c)
        lg.setColorAt(0.6, color)
        lg.setColorAt(1, bot_c)
        p.setBrush(lg)
        p.setPen(Qt.NoPen)
        p.drawPath(grad_path)
        p.setPen(QPen(color.lighter(150), 1.0))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, sz - 2, sz - 2, r - 1, r - 1)
        p.setPen(QColor(255, 255, 255))
        font = QFont("Microsoft YaHei")
        font.setBold(True)
        font.setPixelSize(int(sz * 0.42))
        p.setFont(font)
        label = name[:1] if name else "?"
        p.drawText(img.rect(), Qt.AlignCenter, label)
        p.end()
        return QPixmap.fromImage(img)

    def get_icon(self, name, subdir="groups", size=None):
        sz = size or self.size
        key = (subdir, name, sz)
        if key in self._cache:
            return self._cache[key]
        pix = None
        if self._icons_available:
            candidates = [
                os.path.join(self.icons_dir, subdir, f"{name}.png"),
                os.path.join(self.icons_dir, subdir, f"{name.replace(' ', '_')}.png"),
            ]
            if subdir == "backgrounds" and name.endswith("_background"):
                base = name[:-len("_background")]
                candidates.append(os.path.join(self.icons_dir, subdir, f"{base}.png"))
            for path in candidates:
                if os.path.isfile(path):
                    pix = QPixmap(path)
                    if not pix.isNull():
                        break
            if pix is None or pix.isNull():
                self._missing.add((subdir, name))
        if pix is None or pix.isNull():
            pix = self._placeholder(subdir, name, sz)
        icon = QIcon(pix)
        self._cache[key] = icon
        return icon

    def get_pixmap(self, name, subdir="groups", size=None):
        icon = self.get_icon(name, subdir, size)
        sz = size or self.size
        return icon.pixmap(QSize(sz, sz))

    def missing_report(self):
        return sorted(self._missing)

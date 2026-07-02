# -*- coding: utf-8 -*-
"""
icon_provider.py
Icon loading with placeholder fallback - upgraded badge-style placeholders.
"""

import os
import re

from PySide6.QtGui import (
    QPixmap, QPainter, QColor, QFont, QIcon, QImage,
    QLinearGradient, QPen, QPainterPath,
)
from PySide6.QtCore import Qt, QSize


PLACEHOLDER_COLORS = {
    "backgrounds": QColor(60, 90, 140),
    "traits": QColor(120, 70, 130),
    "groups": QColor(70, 120, 90),
    "default": QColor(90, 90, 90),
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
        self._missing = set()
        self._icons_available = os.path.isdir(icons_dir)
        self._perk_icon_map = {}
        if self._icons_available:
            self._build_perk_map()

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
        for candidate in (norm, compact):
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
        result = pix if (pix and not pix.isNull()) else QPixmap(size, size)
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

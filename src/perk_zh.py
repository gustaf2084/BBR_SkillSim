# -*- coding: utf-8 -*-
"""perk_zh.py — 技能名称和描述的中英映射.

数据存储于 perk_i18n.json，本模块为薄封装层。
英文描述直接取自 data.json perk_trees,中文按英文原文完整直译.
"""

import json
import os
import sys


def _app_dir():
    """Return the directory containing data files (supports PyInstaller frozen)."""
    if getattr(sys, "frozen", False):
        # PyInstaller onefile: bundled data is extracted to sys._MEIPASS
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _load_i18n():
    """加载 perk_i18n.json，返回 (name_map, desc_map) 两个字典。"""
    path = os.path.join(_app_dir(), "perk_i18n.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        # 返回空映射作为降级（翻译缺失时显示英文原名）
        return {}, {}

    name_map = {}
    desc_map = {}
    for en_name, entry in raw.items():
        zh_name = entry.get("zh")
        zh_desc = entry.get("desc_zh")
        if zh_name:
            name_map[en_name] = zh_name
        if zh_desc:
            desc_map[en_name] = zh_desc
    return name_map, desc_map


_NAME_MAP, _DESC_MAP = _load_i18n()


def get_perk_name_zh(en_name):
    """获取技能的中文名，无翻译时返回原名。"""
    return _NAME_MAP.get(en_name, en_name)


def get_perk_desc_zh(en_name):
    """获取技能的中文描述，无翻译时返回空字符串。"""
    return _DESC_MAP.get(en_name, "")


def get_perk_name_en(en_name):
    """英文模式下直接返回英文名（即键）。"""
    return en_name


def get_perk_desc_en(en_name):
    """英文模式下返回英文原文描述。

    英文原文存储在 data.json 的 perk_trees 中（格式 "名字\\n描述"）。
    本函数仅作占位；实际英文描述由 widget 使用 skill_desc 字段。
    """
    return ""

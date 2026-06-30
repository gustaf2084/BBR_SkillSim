# -*- coding: utf-8 -*-
"""data_loader.py - load & validate data.json, provide GameData object."""

import json, os
from collections import OrderedDict

class DataError(Exception):
    def __init__(self, message, code="format", detail=None):
        super().__init__(message)
        self.code = code
        self.detail = detail

class IconError(Exception):
    pass

TOP_KEYS = ["meta","config","backgrounds","traits","groups",
            "exclusive_groups","attribute_weights","projected_attributes",
            "perk_trees","builds"]
REQUIRED_BG_FIELDS = ["display_zh","group_rolls","multipliers",
                       "melee_only","exclusive","base_probabilities","icon"]
REQUIRED_TRAIT_FIELDS = ["display_zh","weights","icon"]

DUPLICATE_BG_GROUPS = [
    ["caravan_hand_background", "caravan_hand_southern_background"],
    ["companion_1h_background", "companion_1h_southern_background",
     "companion_2h_background", "companion_2h_southern_background",
     "companion_ranged_background", "companion_ranged_southern_background"],
]

def _build_excluded():
    excluded = set()
    for group in DUPLICATE_BG_GROUPS:
        for bg_id in group[1:]:
            excluded.add(bg_id)
    return excluded

EXCLUDED_BACKGROUNDS = _build_excluded()

SETTINGS_FILE = "settings.json"


def _load_settings(app_dir):
    path = os.path.join(app_dir, SETTINGS_FILE)
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_settings(app_dir, data):
    path = os.path.join(app_dir, SETTINGS_FILE)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class GameData:
    def __init__(self, data, path, warnings=None, lang="zh"):
        self._data = data
        self._path = path
        self.warnings = warnings or []
        self.lang = lang

    @property
    def meta(self): return self._data.get("meta", {})
    @property
    def version(self): return self.meta.get("version", "")
    @property
    def config(self): return self._data.get("config", {})
    @property
    def max_level(self): return self.config.get("max_level", 11)
    @property
    def skill_points(self): return self.config.get("skill_points", 10)
    @property
    def big_weight(self): return self.config.get("big_weight", 10.0)
    @property
    def default_group_rolls(self): return self.config.get("default_group_rolls", {})
    @property
    def backgrounds(self): return self._data.get("backgrounds", {})
    @property
    def traits(self): return self._data.get("traits", {})
    @property
    def groups(self): return self._data.get("groups", {})
    @property
    def exclusive_groups(self): return self._data.get("exclusive_groups", {})
    @property
    def attribute_weights(self): return self._data.get("attribute_weights", {})
    @property
    def projected_attributes(self): return self._data.get("projected_attributes", {})
    @property
    def perk_trees(self): return self._data.get("perk_trees", {})
    @property
    def builds(self): return self._data.get("builds", {})

    def set_lang(self, lang):
        self.lang = lang

    def group_category(self, group_name):
        g = self.groups.get(group_name)
        return g["category"] if g else None

    def groups_by_category(self, category):
        result = []
        for gname, gdef in self.groups.items():
            if gdef.get("category") == category:
                result.append((gdef.get("order", 999), gname))
        result.sort()
        return [g for _, g in result]

    def category_order(self):
        return ["Shared","Exclusive","Weapon","Armor","Fighting Style","Special"]

    def is_background_complete(self, bg_id):
        bg = self.backgrounds.get(bg_id)
        if not bg:
            return False
        for f in REQUIRED_BG_FIELDS:
            if f not in bg:
                return False
        return True

    def is_background_excluded(self, bg_id):
        return bg_id in EXCLUDED_BACKGROUNDS

    def bg_name(self, bg_id):
        if self.lang == "en":
            return bg_id
        return self.backgrounds.get(bg_id, {}).get("display_zh") or bg_id

    def trait_name(self, trait_id):
        if self.lang == "en":
            return trait_id
        return self.traits.get(trait_id, {}).get("display_zh") or trait_id

    def group_name(self, group_id):
        if self.lang == "en":
            return group_id
        return self.groups.get(group_id, {}).get("display_zh") or group_id

    def get_perk_tree(self, group_id):
        return self.perk_trees.get(group_id, {})

    def complete_backgrounds(self):
        return sorted([b for b in self.backgrounds
                       if self.is_background_complete(b)])

    def filtered_complete_backgrounds(self):
        return sorted([b for b in self.backgrounds
                       if self.is_background_complete(b)
                       and not self.is_background_excluded(b)])

    def incomplete_backgrounds(self):
        return sorted([b for b in self.backgrounds
                       if not self.is_background_complete(b)])


def load_data(data_path, expected_version="0.7.6", strict=False, lang="zh"):
    if not os.path.exists(data_path):
        raise DataError("data.json not found: " + data_path, code="missing")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            raw = json.load(f, object_pairs_hook=OrderedDict)
    except json.JSONDecodeError as e:
        raise DataError(
            "JSON error line {} col {}: {}".format(e.lineno, e.colno, e.msg),
            code="format")
    except Exception as e:
        raise DataError("Read error: {}".format(e), code="format")
    missing = [k for k in TOP_KEYS if k not in raw]
    if missing:
        raise DataError("Missing keys: " + ", ".join(missing), code="schema")
    warnings = []
    ver = raw.get("meta", {}).get("version", "")
    if ver != expected_version:
        warnings.append("Version {} != expected {}".format(ver, expected_version))
    for bid, bd in raw.get("backgrounds", {}).items():
        for f in REQUIRED_BG_FIELDS:
            if f not in bd:
                warnings.append("bg {} missing {}".format(bid, f))
    for tid, td in raw.get("traits", {}).items():
        for f in REQUIRED_TRAIT_FIELDS:
            if f not in td:
                warnings.append("trait {} missing {}".format(tid, f))
    gids = set(raw.get("groups", {}).keys())
    refs = set()
    for bd in raw.get("backgrounds", {}).values():
        refs.update(bd.get("multipliers", {}).keys())
        refs.update(bd.get("base_probabilities", {}).keys())
    for td in raw.get("traits", {}).values():
        refs.update(td.get("weights", {}).keys())
    for g in refs:
        if g not in gids:
            warnings.append("group {} referenced but not defined".format(g))
    if strict and warnings:
        raise DataError(
            "Validation: " + "; ".join(warnings[:5]),
            code="incomplete", detail=warnings)
    return GameData(raw, data_path, warnings, lang=lang)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "data.json")
    try:
        gd = load_data(path)
        print("OK", gd.version, "bg:", len(gd.backgrounds), "traits:", len(gd.traits))
        if gd.warnings:
            print("  warnings:", len(gd.warnings))
    except DataError as e:
        print("FAIL:", e.code, e)

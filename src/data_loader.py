# -*- coding: utf-8 -*-
"""data_loader.py - load & validate data.json, provide GameData object."""

import json, os
from collections import OrderedDict
from typing import Any


class DataError(Exception):
    def __init__(self, message: str, code: str = "format", detail: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.detail = detail


class IconError(Exception):
    pass


TOP_KEYS: list[str] = ["meta","config","backgrounds","traits","groups",
            "exclusive_groups","attribute_weights","projected_attributes",
            "perk_trees","builds"]
REQUIRED_BG_FIELDS: list[str] = ["display_zh","group_rolls","multipliers",
                       "melee_only","exclusive","base_probabilities","icon"]
REQUIRED_TRAIT_FIELDS: list[str] = ["display_zh","weights","icon"]

DUPLICATE_BG_GROUPS: list[list[str]] = [
    ["caravan_hand_background", "caravan_hand_southern_background"],
]

HIDDEN_BACKGROUNDS: list[str] = [
    "companion_1h_background", "companion_1h_southern_background",
    "companion_2h_background", "companion_2h_southern_background",
    "companion_ranged_background", "companion_ranged_southern_background",
]


def _build_excluded() -> set[str]:
    excluded: set[str] = set()
    for group in DUPLICATE_BG_GROUPS:
        for bg_id in group[1:]:
            excluded.add(bg_id)
    excluded.update(HIDDEN_BACKGROUNDS)
    return excluded


EXCLUDED_BACKGROUNDS: set[str] = _build_excluded()

SETTINGS_FILE: str = "settings.json"


def _load_settings(app_dir: str) -> dict[str, Any]:
    path: str = os.path.join(app_dir, SETTINGS_FILE)
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_settings(app_dir: str, data: dict[str, Any]) -> None:
    path: str = os.path.join(app_dir, SETTINGS_FILE)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class GameData:
    def __init__(self,
                 data: dict[str, Any],
                 path: str,
                 warnings: list[str] | None = None,
                 lang: str = "zh",
                 lazy_perk_trees: bool = False) -> None:
        self._data = data
        self._path = path
        self.warnings = warnings or []
        self.lang = lang
        self._perk_trees: dict[str, Any] | None = None if lazy_perk_trees else data.get("perk_trees", {})
        self._perk_trees_path: str = os.path.join(os.path.dirname(path), "perk_trees.json")

    @property
    def meta(self) -> dict[str, Any]: return self._data.get("meta", {})
    @property
    def version(self) -> str: return self.meta.get("version", "")
    @property
    def config(self) -> dict[str, Any]: return self._data.get("config", {})
    @property
    def max_level(self) -> int: return self.config.get("max_level", 11)
    @property
    def skill_points(self) -> int: return self.config.get("skill_points", 10)
    @property
    def big_weight(self) -> float: return self.config.get("big_weight", 10.0)
    @property
    def default_group_rolls(self) -> dict[str, Any]: return self.config.get("default_group_rolls", {})
    @property
    def backgrounds(self) -> dict[str, Any]: return self._data.get("backgrounds", {})
    @property
    def traits(self) -> dict[str, Any]: return self._data.get("traits", {})
    @property
    def groups(self) -> dict[str, Any]: return self._data.get("groups", {})
    @property
    def exclusive_groups(self) -> dict[str, Any]: return self._data.get("exclusive_groups", {})
    @property
    def attribute_weights(self) -> dict[str, Any]: return self._data.get("attribute_weights", {})
    @property
    def projected_attributes(self) -> dict[str, Any]: return self._data.get("projected_attributes", {})
    @property
    def perk_trees(self) -> dict[str, Any]:
        if self._perk_trees is None:
            self._load_perk_trees_file()
        return self._perk_trees or {}

    def _load_perk_trees_file(self) -> None:
        """Lazy-load perk_trees from separate JSON file."""
        if os.path.exists(self._perk_trees_path):
            try:
                with open(self._perk_trees_path, "r", encoding="utf-8") as f:
                    self._perk_trees = json.load(f, object_pairs_hook=OrderedDict)
            except Exception:
                self._perk_trees = {}
        else:
            self._perk_trees = self._data.get("perk_trees", {})
    @property
    def builds(self) -> dict[str, Any]: return self._data.get("builds", {})

    def set_lang(self, lang: str) -> None:
        self.lang = lang

    def group_category(self, group_name: str) -> str | None:
        g: dict[str, Any] | None = self.groups.get(group_name)
        return g["category"] if g else None

    def groups_by_category(self, category: str) -> list[str]:
        result: list[tuple[int, str]] = []
        for gname, gdef in self.groups.items():
            if gdef.get("category") == category:
                result.append((gdef.get("order", 999), gname))
        result.sort()
        return [g for _, g in result]

    def category_order(self) -> list[str]:
        return ["Shared","Exclusive","Weapon","Armor","Fighting Style","Special"]

    def is_background_complete(self, bg_id: str) -> bool:
        bg: dict[str, Any] | None = self.backgrounds.get(bg_id)
        if not bg:
            return False
        for f in REQUIRED_BG_FIELDS:
            if f not in bg:
                return False
        return True

    def is_background_excluded(self, bg_id: str) -> bool:
        return bg_id in EXCLUDED_BACKGROUNDS

    @staticmethod
    def _en_display_name(bg_id: str) -> str:
        s = bg_id
        if s.endswith("_background"):
            s = s[: -len("_background")]
        if s.startswith("rf_"):
            s = s[len("rf_"):]
        southern = False
        if s.endswith("_southern"):
            southern = True
            s = s[: -len("_southern")]
        SMALL = {"on", "the", "of", "for", "in", "and", "to", "a", "an"}

        def _cap(p: str) -> str:
            if p in SMALL:
                return p
            if p == "1h":
                return "1H"
            if p == "2h":
                return "2H"
            return p.capitalize()

        parts = [p for p in s.split("_") if p]
        name = " ".join(_cap(p) for p in parts)
        if name == "Kings Guard":
            name = "King\'s Guard"
        if southern:
            name = "Southern " + name
        return name

    def bg_name(self, bg_id: str) -> str:
        if self.lang == "en":
            return self._en_display_name(bg_id)
        return self.backgrounds.get(bg_id, {}).get("display_zh") or bg_id

    def trait_name(self, trait_id: str) -> str:
        if self.lang == "en":
            return trait_id
        return self.traits.get(trait_id, {}).get("display_zh") or trait_id

    def group_name(self, group_id: str) -> str:
        if self.lang == "en":
            return group_id
        return self.groups.get(group_id, {}).get("display_zh") or group_id

    def get_perk_tree(self, group_id: str) -> dict[str, Any]:
        return self.perk_trees.get(group_id, {})

    def complete_backgrounds(self) -> list[str]:
        return sorted([b for b in self.backgrounds
                       if self.is_background_complete(b)])

    def filtered_complete_backgrounds(self) -> list[str]:
        return sorted([b for b in self.backgrounds
                       if self.is_background_complete(b)
                       and not self.is_background_excluded(b)])

    def incomplete_backgrounds(self) -> list[str]:
        return sorted([b for b in self.backgrounds
                       if not self.is_background_complete(b)])

    # ── v0.3.0: Background attribute range accessors ──────────────

    def bg_attributes(self, bg_id: str) -> dict[str, list[int]] | None:
        """Return the 8-attribute min-max range for a background, or None if no data."""
        bg = self.backgrounds.get(bg_id)
        if not bg:
            return None
        return bg.get("attributes")

    def bg_attribute_estimated(self, bg_id: str) -> bool:
        """Whether the background's attribute ranges are estimated (fallback, non-authoritative)."""
        bg = self.backgrounds.get(bg_id)
        if not bg:
            return False
        return bg.get("attributes_estimated", False)

    def bg_attribute_missing(self, bg_id: str) -> bool:
        """Whether the background's attribute ranges are completely missing (mod-added, no data)."""
        bg = self.backgrounds.get(bg_id)
        if not bg:
            return True
        return bool(bg.get("attributes_missing")) or (
            bg.get("attributes") is None and not self.bg_attribute_estimated(bg_id))

    def talent_levelup_ranges(self) -> dict:
        """Return the talent level-up ranges {attribute: {star_level: [min, max]}}."""
        return self._data.get("talent_levelup_ranges", {})

    def talent_star_distribution(self) -> dict:
        """Return the talent star probability distribution (e.g. {"1":0.6,"2":0.3,"3":0.1})."""
        return self._data.get("talent_star_distribution", {"1": 0.6, "2": 0.3, "3": 0.1})

    def talent_excluded_attributes(self) -> dict:
        """Return backgrounds with excluded talent attributes {bg_id: [attr,...]}."""
        return self._data.get("talent_excluded_attributes", {})


def load_data(data_path: str,
              expected_version: str = "0.7.6",
              strict: bool = False,
              strict_version: bool = True,
              lang: str = "zh",
              lazy_perk_trees: bool = True) -> GameData:
    if not os.path.exists(data_path):
        raise DataError("data.json not found: " + data_path, code="missing")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            raw: OrderedDict = json.load(f, object_pairs_hook=OrderedDict)
    except json.JSONDecodeError as e:
        raise DataError(
            "JSON error line {} col {}: {}".format(e.lineno, e.colno, e.msg),
            code="format")
    except Exception as e:
        raise DataError("Read error: {}".format(e), code="format")
    missing: list[str] = [k for k in TOP_KEYS if k not in raw]
    if missing:
        raise DataError("Missing keys: " + ", ".join(missing), code="schema")
    warnings: list[str] = []
    ver: str = raw.get("meta", {}).get("version", "")
    if ver != expected_version:
        msg: str = f"Data version '{ver}' != expected '{expected_version}'. Update data.json or pass strict_version=False to continue."
        if strict_version:
            raise DataError(msg, code="version", detail={"actual": ver, "expected": expected_version})
        warnings.append("Version {} != expected {}".format(ver, expected_version))
    for bid, bd in raw.get("backgrounds", {}).items():
        for f in REQUIRED_BG_FIELDS:
            if f not in bd:
                warnings.append("bg {} missing {}".format(bid, f))
    for tid, td in raw.get("traits", {}).items():
        for f in REQUIRED_TRAIT_FIELDS:
            if f not in td:
                warnings.append("trait {} missing {}".format(tid, f))
    gids: set[str] = set(raw.get("groups", {}).keys())
    refs: set[str] = set()
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
    return GameData(raw, data_path, warnings, lang=lang,
                    lazy_perk_trees=lazy_perk_trees)


def load_perk_trees(data_dir: str) -> dict[str, Any]:
    path: str = os.path.join(data_dir, "perk_trees.json")
    if not os.path.exists(path):
        data_path: str = os.path.join(data_dir, "data.json")
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                raw: OrderedDict = json.load(f, object_pairs_hook=OrderedDict)
            return raw.get("perk_trees", {})
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)


if __name__ == "__main__":
    here: str = os.path.dirname(os.path.abspath(__file__))
    path: str = os.path.join(here, "data.json")
    try:
        gd: GameData = load_data(path)
        print("OK", gd.version, "bg:", len(gd.backgrounds), "traits:", len(gd.traits))
        if gd.warnings:
            print("  warnings:", len(gd.warnings))
    except DataError as e:
        print("FAIL:", e.code, e)

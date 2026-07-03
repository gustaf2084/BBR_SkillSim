# -*- coding: utf-8 -*-
"""Regression tests for perk translation lookup and displayed tier placement."""

import json
import re
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
_src = _root / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from perk_zh import get_perk_desc_zh, get_perk_name_zh

PERK_TREES_PATH = _src / "perk_trees.json"
DOCS_PATH = _src / "docs"

ALIASES = {
    "coup_de_grace": "executioner",
    "fast_adaption": "fast_adaptation",
}


def _load_perk_trees():
    with PERK_TREES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _has_cjk(text):
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def _perk_name(perk_raw):
    return perk_raw.split("\n", 1)[0].strip()


def _has_desc(perk_raw):
    return "\n" in perk_raw and bool(perk_raw.split("\n", 1)[1].strip())


def _canonical_slug(slug):
    slug = ALIASES.get(slug, slug)
    if slug.startswith("swordmaster_"):
        slug = slug[len("swordmaster_"):]
    return slug


def _name_to_slug(name):
    base = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip().replace("'", "")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_").lower()
    return _canonical_slug(slug)


def _perk_id_to_slug(perk_id):
    slug = perk_id.strip()
    if slug.startswith("perk."):
        slug = slug[len("perk."):]
    if slug.startswith("rf_"):
        slug = slug[len("rf_"):]
    if slug.startswith("mastery."):
        slug = slug.split(".", 1)[1] + "_mastery"
    slug = slug.replace(".", "_")
    return _canonical_slug(slug)


def _suffix_to_group(suffix):
    return " ".join(part.capitalize() for part in suffix.split("_"))


def _load_source_tiers():
    source = {}
    for path in DOCS_PATH.rglob("*.nut"):
        if "perk_groups" not in path.parts:
            continue

        stem = path.stem
        if stem.startswith("pg_rf_"):
            group = _suffix_to_group(stem[len("pg_rf_"):])
        elif stem.startswith("pg_special_rf_"):
            group = _suffix_to_group(stem[len("pg_special_rf_"):])
        else:
            continue

        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"this\.m\.Tree\s*=\s*\[(.*?)\]\s*;", text, re.S)
        if not match:
            continue

        tiers = {}
        for row, row_text in enumerate(re.findall(r"\[(.*?)\]", match.group(1), re.S), start=1):
            perk_ids = re.findall(r'"([^"]+)"', row_text)
            if perk_ids:
                tiers[f"Tier {row}"] = [_perk_id_to_slug(perk_id) for perk_id in perk_ids]
        source[group] = tiers
    return source


def test_shield_tier_2_and_4_have_chinese_translations():
    names = [
        "Phalanx (requires Two-Handed Weapon with Piercing Attack, or Shield)",
        "Line Breaker (requires Shield)",
    ]
    for name in names:
        zh_name = get_perk_name_zh(name)
        zh_desc = get_perk_desc_zh(name)
        assert zh_name != name
        assert _has_cjk(zh_name)
        assert _has_cjk(zh_desc)


def test_perk_lookup_handles_qualifier_variants():
    cases = [
        "Dismantle (requires Cutting Attack with Axe)",
        "Nailed It (requires Ranged attack)",
        "Offhand Training (requires Offhand Item weighing less than 10)",
    ]
    for name in cases:
        assert get_perk_name_zh(name) != name
        assert _has_cjk(get_perk_desc_zh(name))


def test_all_displayed_perks_have_chinese_names_and_descriptions():
    missing_names = []
    missing_descs = []

    for group, tiers in _load_perk_trees().items():
        for tier, perk_raw in tiers.items():
            if not isinstance(perk_raw, str) or not perk_raw.strip():
                continue
            name = _perk_name(perk_raw)
            zh_name = get_perk_name_zh(name)
            if zh_name == name or not _has_cjk(zh_name):
                missing_names.append(f"{group} {tier}: {name}")
            if _has_desc(perk_raw) and not _has_cjk(get_perk_desc_zh(name)):
                missing_descs.append(f"{group} {tier}: {name}")

    assert missing_names == []
    assert missing_descs == []


def test_displayed_perk_tiers_match_source_perk_groups():
    source = _load_source_tiers()
    mismatches = []

    for group, tiers in _load_perk_trees().items():
        if group == "General":
            continue
        assert group in source, f"Missing source perk group for {group}"

        for tier, perk_raw in tiers.items():
            if not isinstance(perk_raw, str) or not perk_raw.strip():
                continue
            name = _perk_name(perk_raw)
            slug = _name_to_slug(name)
            source_slugs = source[group].get(tier, [])
            if slug not in source_slugs:
                mismatches.append(f"{group} {tier}: {name} not in {source_slugs}")

    assert mismatches == []

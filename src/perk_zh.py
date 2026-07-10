# -*- coding: utf-8 -*-
"""Chinese perk name and description lookup.

The source data is stored in perk_i18n.json.  Perk names in perk_trees.json
sometimes differ only by qualifier spelling, for example:

    Line Breaker (requires Shield)
    Line Breaker (Requires Shield)

or by whether the qualifier includes the leading "requires".  The lookup layer
normalizes those forms so Chinese UI does not fall back to English text.
"""

import json
import re

from app_paths import resolve_resource

_QUALIFIER_RE = re.compile(r"\s*\(([^)]*)\)\s*$")
_ZH_QUALIFIER_RE = re.compile(r"\s*[\(（][^()（）]*[\)）]\s*$")
_REQUIRES_RE = re.compile(r"^requires\s+", re.IGNORECASE)


def _squash_spaces(value):
    return re.sub(r"\s+", " ", value).strip().lower()


def _split_qualifier(en_name):
    """Return (base, qualifier) for a perk display name."""
    name = en_name.strip()
    match = _QUALIFIER_RE.search(name)
    if not match:
        return name, ""
    base = name[: match.start()].strip()
    qualifier = match.group(1).strip()
    return base, qualifier


def _normalized_base_key(en_name):
    base, _ = _split_qualifier(en_name)
    return _squash_spaces(base)


def _normalized_full_key(en_name):
    base, qualifier = _split_qualifier(en_name)
    base_key = _squash_spaces(base)
    if not qualifier:
        return base_key
    qualifier = _REQUIRES_RE.sub("", qualifier).strip()
    qualifier_key = _squash_spaces(qualifier)
    return f"{base_key} ({qualifier_key})"


def _strip_zh_qualifier(zh_name):
    return _ZH_QUALIFIER_RE.sub("", zh_name).strip()


def _add_if_absent(mapping, key, value):
    if key and value and key not in mapping:
        mapping[key] = value


def _register_translation(mapping, en_name, value, *, strip_zh=False):
    """Register exact, normalized-full, and base-name lookup keys."""
    if not value:
        return

    base_value = _strip_zh_qualifier(value) if strip_zh else value
    mapping[("exact", en_name)] = value
    _add_if_absent(mapping, ("full", _normalized_full_key(en_name)), value)
    _add_if_absent(mapping, ("base", _normalized_base_key(en_name)), base_value)


def _load_i18n():
    """Load perk_i18n.json and return name/description lookup maps."""
    path = resolve_resource("perk_i18n.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        # Degrade gracefully: callers will show the original English name.
        return {}, {}

    name_map = {}
    desc_map = {}
    for en_name, entry in raw.items():
        _register_translation(name_map, en_name, entry.get("zh"), strip_zh=True)
        _register_translation(desc_map, en_name, entry.get("desc_zh"))
    return name_map, desc_map


def _lookup(mapping, en_name, fallback):
    exact = mapping.get(("exact", en_name))
    if exact:
        return exact

    full = mapping.get(("full", _normalized_full_key(en_name)))
    if full:
        return full

    base = mapping.get(("base", _normalized_base_key(en_name)))
    if base:
        return base

    return fallback


_NAME_MAP, _DESC_MAP = _load_i18n()


def get_perk_name_zh(en_name):
    """Return a perk's Chinese name, or the original English name if missing."""
    return _lookup(_NAME_MAP, en_name, en_name)


def get_perk_desc_zh(en_name):
    """Return a perk's Chinese description, or an empty string if missing."""
    return _lookup(_DESC_MAP, en_name, "")


def get_perk_name_en(en_name):
    """English mode uses the original English display name."""
    return en_name


def get_perk_desc_en(en_name):
    """English descriptions are supplied directly by the skill tree widget."""
    return ""

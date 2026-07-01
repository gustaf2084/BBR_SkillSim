# -*- coding: utf-8 -*-
"""Unit tests for data_loader.py - GameData loading and validation."""

import sys
import os
import json
import tempfile
import pytest

_src = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(_src))

from data_loader import load_data, GameData, DataError, HIDDEN_BACKGROUNDS, EXCLUDED_BACKGROUNDS

DATA_PATH = os.path.join(os.path.abspath(_src), "data.json")


@pytest.fixture(scope="module")
def gd():
    return load_data(DATA_PATH, strict_version=False, lang="zh")


@pytest.fixture
def temp_json():
    files = []
    def _make(content, name="test_data.json"):
        tmp = os.path.join(tempfile.gettempdir(), name)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False)
        files.append(tmp)
        return tmp
    yield _make
    for f in files:
        if os.path.exists(f):
            os.remove(f)


class TestLoadData:
    def test_load_data_valid(self, gd):
        assert isinstance(gd, GameData)
        assert gd.version == "0.7.6"

    def test_load_data_with_warnings(self):
        gd = load_data(DATA_PATH, expected_version="9.9.9",
                        strict_version=False, lang="zh")
        assert isinstance(gd, GameData)
        assert len(gd.warnings) >= 1
        assert any("9.9.9" in w for w in gd.warnings)

    def test_load_data_missing_file(self):
        with pytest.raises(DataError) as excinfo:
            load_data("/nonexistent/path/data.json")
        assert excinfo.value.code == "missing"

    def test_load_data_invalid_json(self, temp_json):
        path = os.path.join(tempfile.gettempdir(), "corrupt.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("{this is not json")
        with pytest.raises(DataError) as excinfo:
            load_data(path)
        assert excinfo.value.code == "format"
        if os.path.exists(path):
            os.remove(path)

    def test_load_data_missing_keys(self, temp_json):
        path = temp_json({"meta": {"version": "0.7.6"}, "config": {}}, name="missing_keys.json")
        with pytest.raises(DataError) as excinfo:
            load_data(path, strict_version=False)
        assert excinfo.value.code == "schema"
        assert "Missing keys" in str(excinfo.value)

    def test_load_data_version_mismatch_raises(self):
        with pytest.raises(DataError) as excinfo:
            load_data(DATA_PATH, expected_version="0.0.0", strict_version=True)
        assert excinfo.value.code == "version"

    def test_load_data_version_mismatch_ok(self):
        gd = load_data(DATA_PATH, expected_version="0.0.0", strict_version=False)
        assert isinstance(gd, GameData)
        has_version_warning = any("0.0.0" in w for w in gd.warnings)
        assert has_version_warning, "Expected version mismatch warning"

    def test_load_data_strict_mode(self, temp_json):
        minimal = {
            "meta": {"version": "0.7.6"},
            "config": {},
            "backgrounds": {},
            "traits": {},
            "groups": {},
            "exclusive_groups": {},
            "attribute_weights": {},
            "projected_attributes": {},
            "perk_trees": {},
            "builds": {},
        }
        path = temp_json(minimal, name="minimal_ok.json")
        gd = load_data(path, strict=True, strict_version=False)
        assert isinstance(gd, GameData)


class TestGameDataProperties:
    def test_backgrounds_count(self, gd):
        assert len(gd.backgrounds) > 50

    def test_traits_count(self, gd):
        assert "Athletic" in gd.traits
        assert "Brute" in gd.traits
        assert "Bloodthirsty" in gd.traits

    def test_groups_count(self, gd):
        assert len(gd.groups) > 30
        for name in ["Dagger", "Bow", "Sword", "Heavy Armor", "Shield", "Knave"]:
            assert name in gd.groups, f"Missing group: {name}"

    def test_groups_by_category(self, gd):
        weapon_groups = gd.groups_by_category("Weapon")
        assert len(weapon_groups) > 5
        assert "Axe" in weapon_groups
        assert "Dagger" in weapon_groups
        orders = [gd.groups[g].get("order", 999) for g in weapon_groups]
        assert orders == sorted(orders), "Groups not sorted by order"

    def test_config_properties(self, gd):
        assert gd.max_level == 11
        assert gd.skill_points == 10
        assert gd.big_weight == 10.0
        assert "Weapon" in gd.default_group_rolls
        assert gd.default_group_rolls["Weapon"] == 3

    def test_exclusive_groups(self, gd):
        assert isinstance(gd.exclusive_groups, dict)

    def test_attribute_weights(self, gd):
        assert isinstance(gd.attribute_weights, dict)

    def test_projected_attributes(self, gd):
        assert isinstance(gd.projected_attributes, dict)

    def test_builds(self, gd):
        assert isinstance(gd.builds, dict)


class TestNames:
    def test_bg_name_zh(self, gd):
        assert gd.bg_name("assassin_background") == "刺客"
        assert gd.bg_name("adventurous_noble_background") == "冒险贵族"

    def test_bg_name_en(self, gd):
        gd.set_lang("en")
        try:
            assert gd.bg_name("assassin_background") == "Assassin"
            assert gd.bg_name("adventurous_noble_background") == "Adventurous Noble"
        finally:
            gd.set_lang("zh")

    def test_trait_name_zh(self, gd):
        assert gd.trait_name("Athletic") == "健壮"
        assert gd.trait_name("Brute") == "粗野"

    def test_trait_name_en(self, gd):
        gd.set_lang("en")
        try:
            assert gd.trait_name("Athletic") == "Athletic"
            assert gd.trait_name("Brute") == "Brute"
        finally:
            gd.set_lang("zh")

    def test_group_name_zh(self, gd):
        assert gd.group_name("Dagger") == "匕首"
        assert gd.group_name("Sword") == "剑"

    def test_group_name_en(self, gd):
        gd.set_lang("en")
        try:
            assert gd.group_name("Dagger") == "Dagger"
            assert gd.group_name("Sword") == "Sword"
        finally:
            gd.set_lang("zh")

    def test_bg_name_fallback(self, gd):
        assert gd.bg_name("nonexistent_bg") == "nonexistent_bg"

    def test_trait_name_fallback(self, gd):
        assert gd.trait_name("nonexistent_trait") == "nonexistent_trait"

    def test_group_name_fallback(self, gd):
        assert gd.group_name("nonexistent_group") == "nonexistent_group"


class TestBackgroundFiltering:
    def test_complete_backgrounds(self, gd):
        bgs = gd.complete_backgrounds()
        assert len(bgs) > 0
        assert "assassin_background" in bgs

    def test_filtered_excludes_hidden(self, gd):
        complete = set(gd.complete_backgrounds())
        filtered = set(gd.filtered_complete_backgrounds())
        for hidden in HIDDEN_BACKGROUNDS:
            if hidden in complete:
                assert hidden not in filtered, f"{hidden} should be excluded"
        assert filtered.issubset(complete)

    def test_filtered_is_sorted(self, gd):
        filtered = gd.filtered_complete_backgrounds()
        assert filtered == sorted(filtered)

    def test_hidden_backgrounds_not_excluded_from_engine(self, gd):
        from engine import SkillEngine
        eng = SkillEngine(gd)
        for hidden in HIDDEN_BACKGROUNDS:
            if hidden not in gd.backgrounds:
                continue
            result = eng.forward_simulate(hidden, [], mode="analytic")
            if result is not None:
                assert "General" in result, f"Hidden bg '{hidden}' should have General=1.0"


class TestVersionValidation:
    def test_version_mismatch_error(self):
        with pytest.raises(DataError) as excinfo:
            load_data(DATA_PATH, expected_version="9.9.9", strict_version=True)
        err = excinfo.value
        assert err.code == "version"
        assert err.detail is not None
        assert err.detail.get("actual") == "0.7.6"
        assert err.detail.get("expected") == "9.9.9"

    def test_version_match_ok(self):
        gd = load_data(DATA_PATH, expected_version="0.7.6", strict_version=True)
        assert gd.version == "0.7.6"

    def test_strict_version_false_warning(self):
        gd = load_data(DATA_PATH, expected_version="9.9.9", strict_version=False)
        assert len(gd.warnings) >= 1
        assert any("9.9.9" in w for w in gd.warnings)


class TestLazyPerkTrees:
    def test_lazy_default_is_true(self):
        gd = load_data(DATA_PATH, strict_version=False, lazy_perk_trees=True)
        assert gd._perk_trees is None

    def test_lazy_property_access(self, gd):
        gd._perk_trees = None
        trees = gd.perk_trees
        assert isinstance(trees, dict)
        assert gd._perk_trees is not None

    def test_lazy_fallback_to_data_json(self):
        gd = load_data(DATA_PATH, strict_version=False, lazy_perk_trees=True)
        orig_path = gd._perk_trees_path
        gd._perk_trees_path = "/nonexistent/perk_trees.json"
        gd._perk_trees = None
        trees = gd.perk_trees
        assert isinstance(trees, dict)
        gd._perk_trees_path = orig_path


class TestGameDataEdgeCases:
    def test_is_background_complete_unknown(self, gd):
        assert gd.is_background_complete("nonexistent") is False

    def test_is_background_complete_known(self, gd):
        assert gd.is_background_complete("assassin_background") is True

    def test_is_background_excluded_known(self, gd):
        for hidden in HIDDEN_BACKGROUNDS:
            assert gd.is_background_excluded(hidden) or hidden not in gd.backgrounds

    def test_group_category(self, gd):
        assert gd.group_category("Dagger") == "Weapon"
        assert gd.group_category("Knave") == "Exclusive"
        assert gd.group_category("Heavy Armor") == "Armor"
        assert gd.group_category("Nonexistent") is None

    def test_category_order(self, gd):
        expected = ["Shared", "Exclusive", "Weapon", "Armor", "Fighting Style", "Special"]
        assert gd.category_order() == expected

    def test_get_perk_tree(self, gd):
        tree = gd.get_perk_tree("Dagger")
        assert isinstance(tree, dict)

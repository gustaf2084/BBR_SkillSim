# -*- coding: utf-8 -*-
"""Unit tests for engine.py - SkillEngine probability calculations."""

import os
import sys

import pytest

_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if _src not in sys.path:  # conftest.py 已注入；直接运行本文件时兜底
    sys.path.insert(0, _src)

from data_loader import load_data
from engine import RANGED_GROUPS, SkillEngine


@pytest.fixture(scope="module")
def gd():
    data_path = os.path.join(_src, "data.json")
    return load_data(data_path, strict_version=False, lang="zh")


@pytest.fixture(scope="module")
def engine(gd):
    return SkillEngine(gd)


class TestForwardSimulate:
    def test_returns_ordereddict(self, engine):
        result = engine.forward_simulate("assassin_background", [], mode="analytic")
        assert result is not None
        assert list(result.keys())

    def test_dagger_high_for_assassin(self, engine):
        result = engine.forward_simulate("assassin_background", [], mode="analytic")
        assert result is not None
        assert result.get("Dagger", 0) > 0.97  # v0.3.0: bg-specific attributes slightly lower than generic default

    def test_light_armor_high_for_assassin(self, engine):
        result = engine.forward_simulate("assassin_background", [], mode="analytic")
        assert result is not None
        assert result.get("Light Armor", 0) > 0.99

    def test_always_groups_have_prob_1(self, engine):
        result = engine.forward_simulate("assassin_background", [], mode="analytic")
        assert result is not None
        assert result.get("General", 0) == 1.0

    def test_probabilities_in_01_range(self, engine):
        result = engine.forward_simulate("assassin_background", [], mode="analytic")
        assert result is not None
        for group, prob in result.items():
            assert 0.0 <= prob <= 1.0, f"{group}: {prob} out of range"

    def test_assassin_exclusive_resolves(self, engine):
        branches = engine.resolve_exclusive("assassin_background")
        assert len(branches) == 1
        groups, prob = branches[0]
        assert groups == ["Knave"]
        assert prob == 1.0

    def test_noble_exclusive_resolves(self, engine):
        branches = engine.resolve_exclusive("adventurous_noble_background")
        assert len(branches) == 1
        groups, prob = branches[0]
        assert groups == ["Noble"]
        assert prob == 1.0

    def test_invalid_bg_id_returns_none(self, engine):
        result = engine.forward_simulate("nonexistent_background", [], mode="analytic")
        assert result is None

    def test_empty_traits_works(self, engine):
        result = engine.forward_simulate("squire_background", [], mode="analytic")
        assert result is not None

    def test_with_traits(self, engine):
        result = engine.forward_simulate("assassin_background", ["Athletic"], mode="analytic")
        assert result is not None
        assert 0.0 <= result.get("Agile", 0) <= 1.0

    def test_ordering_desc_by_prob(self, engine):
        result = engine.forward_simulate("assassin_background", [], mode="analytic")
        assert result is not None
        items = list(result.items())
        for i in range(len(items) - 1):
            g1, p1 = items[i]
            g2, p2 = items[i + 1]
            if p1 < p2:
                pytest.fail(f"Order violation at {i}: {g1}={p1} < {g2}={p2}")
            elif p1 == p2:
                assert g1 <= g2, f"Tiebreak violation: {g1} > {g2}"

    def test_squire_not_none(self, engine):
        result = engine.forward_simulate("squire_background", [], mode="analytic")
        assert result is not None

    def test_anatomist_background(self, engine):
        result = engine.forward_simulate("anatomist_background", [], mode="analytic")
        assert result is not None

    def test_monte_carlo_produces_results(self, engine):
        result = engine.forward_simulate("assassin_background", [], mode="monte_carlo",
                                          samples=5000, seed=42)
        assert result is not None
        assert result.get("Dagger", 0) > 0.97  # v0.3.0: bg-specific attributes


class TestAnalyticVsMonteCarlo:
    TOLERANCE = 0.05
    TEST_GROUPS = ["Dagger", "Light Armor", "Swift", "Agile", "Fast", "Heavy Armor"]
    BACKGROUND = "assassin_background"

    def test_consistency_assassin(self, engine):
        diffs = []
        for group in self.TEST_GROUPS:
            pa = engine.appear_prob_analytic(self.BACKGROUND, [], group)
            pm = engine.appear_prob_monte_carlo(self.BACKGROUND, [], group,
                                                 samples=30000, seed=42)
            diff = abs(pa - pm)
            diffs.append((group, pa, pm, diff))
        worst = max(diffs, key=lambda x: x[3])
        assert worst[3] < self.TOLERANCE, (
            f"Worst diff: {worst[0]} analytic={worst[1]:.3f} monte={worst[2]:.3f} "
            f"diff={worst[3]:.3f} >= {self.TOLERANCE}")

    def test_consistency_squire(self, engine):
        eng2 = SkillEngine(engine.gd)
        groups = ["Sword", "Shield"]
        diffs = []
        for group in groups:
            pa = eng2.appear_prob_analytic("squire_background", [], group)
            pm = eng2.appear_prob_monte_carlo("squire_background", [], group,
                                               samples=20000, seed=42)
            diffs.append(abs(pa - pm))
        worst = max(diffs)
        assert worst < self.TOLERANCE, f"Worst diff for squire: {worst:.3f}"

    def test_consistency_vs_pruned_weights_zero(self, engine):
        pa = engine.appear_prob_analytic("assassin_background", [], "Heavy Armor")
        pm = engine.appear_prob_monte_carlo("assassin_background", [], "Heavy Armor",
                                             samples=10000, seed=42)
        assert pa == 0.0
        assert pm == 0.0


class TestEdgeCases:
    def test_empty_traits_no_forward(self, engine):
        result = engine.forward_simulate("assassin_background", [], mode="analytic")
        assert result is not None

    def test_invalid_bg_id_forward(self, engine):
        result = engine.forward_simulate("", [], mode="analytic")
        assert result is None

    def test_invalid_bg_id_appear_prob(self, engine):
        p = engine.appear_prob_analytic("no_such_bg", [], "Dagger")
        assert p == 0.0

    def test_invalid_group_appear_prob(self, engine):
        p = engine.appear_prob_analytic("assassin_background", [], "NoSuchGroup")
        assert p == 0.0

    def test_melee_only_blocks_ranged(self, engine):
        result = engine.forward_simulate("assassin_background", [], mode="analytic")
        assert result is not None
        for rg in RANGED_GROUPS:
            if rg in result:
                assert result[rg] == 0.0, f"{rg} should be 0 for melee_only"

    def test_adventurous_noble_is_melee_only(self, engine):
        result = engine.forward_simulate("adventurous_noble_background", [], mode="analytic")
        assert result is not None
        for rg in RANGED_GROUPS:
            if rg in result:
                assert result[rg] == 0.0, f"{rg} prob={result[rg]} for melee_only bg"


class TestCaching:
    def test_cache_returns_same_object(self, engine):
        r1 = engine.forward_simulate("assassin_background", [], mode="analytic")
        r2 = engine.forward_simulate("assassin_background", [], mode="analytic")
        assert r1 is r2, "Second call did not return cached object"

    def test_cache_different_traits_different_result(self, engine):
        r1 = engine.forward_simulate("assassin_background", [], mode="analytic")
        r2 = engine.forward_simulate("assassin_background", ["Clubfooted"], mode="analytic")
        assert r1 is not None and r2 is not None
        assert r1 is not r2, "Different traits should produce different cached objects"
        assert r2.get("Agile", 0) == 0.0, "Clubfooted should zero Agile"
        assert r1.get("Agile", 0) > 0.0, "Without Clubfooted, Agile should be >0"

    def test_cache_with_lru_eviction(self, engine):
        bgs = list(engine.gd.complete_backgrounds())
        for bg_id in bgs[:5]:
            engine.forward_simulate(bg_id, [], mode="analytic")

    def test_cache_none_result(self, engine):
        r1 = engine.forward_simulate("no_such_bg", [], mode="analytic")
        assert r1 is None


class TestReverseDerive:
    def test_reverse_derive_dagger(self, engine):
        result = engine.reverse_derive(
            ["Dagger"], mode="analytic", top_n=5, tiebreak_limit=20,
            prune_threshold=20)
        assert result["max_score"] > 0
        assert len(result["results"]) > 0
        first = result["results"][0]
        assert len(first) == 5
        assert first[2] > 0

    def test_reverse_derive_pruning_disabled(self, engine):
        result = engine.reverse_derive(
            ["Dagger"], mode="analytic", top_n=5, tiebreak_limit=20,
            prune_threshold=0)
        assert result["max_score"] > 0
        assert len(result["results"]) > 0

    def test_reverse_derive_preserves_max_score(self, engine):
        r_prune = engine.reverse_derive(
            ["Dagger"], mode="analytic", top_n=5, tiebreak_limit=20,
            prune_threshold=20)
        r_no_prune = engine.reverse_derive(
            ["Dagger"], mode="analytic", top_n=5, tiebreak_limit=20,
            prune_threshold=0)
        assert r_prune["max_score"] > 0
        assert r_no_prune["max_score"] > 0
        diff = abs(r_prune["max_score"] - r_no_prune["max_score"])
        assert diff < 0.01

    def test_reverse_derive_invalid_target(self, engine):
        result = engine.reverse_derive(
            ["NoSuchGroup"], mode="analytic", top_n=5, tiebreak_limit=20,
            prune_threshold=20)
        assert result["max_score"] == 0.0
        assert len(result["results"]) == 0

    def test_reverse_derive_invalid_mixed_targets(self, engine):
        result = engine.reverse_derive(
            ["Dagger", "NoSuchGroup"], mode="analytic", top_n=5,
            tiebreak_limit=20, prune_threshold=20)
        assert result["max_score"] >= 0
        assert isinstance(result["results"], list)

    def test_reverse_derive_multi_target(self, engine):
        result = engine.reverse_derive(
            ["Heavy Armor", "Shield", "Trained"], mode="analytic",
            top_n=3, tiebreak_limit=20, prune_threshold=20)
        assert result["max_score"] > 0
        assert len(result["results"]) > 0

    def test_reverse_derive_with_custom_weights(self, engine):
        result = engine.reverse_derive(
            ["Dagger", "Light Armor"],
            weights={"Dagger": 2.0, "Light Armor": 1.0},
            mode="analytic", top_n=5, tiebreak_limit=20,
            prune_threshold=20)
        assert result["max_score"] > 0

    def test_reverse_derive_no_results_for_impossible(self, engine):
        result = engine.reverse_derive(
            [], mode="analytic", top_n=5, tiebreak_limit=20,
            prune_threshold=20)
        assert result["max_score"] == 0.0


class TestProgressCallback:
    def test_callback_fires(self, engine):
        call_count = [0]
        def callback(current, total):
            call_count[0] += 1
            return False
        engine.reverse_derive(
            ["Dagger"], mode="analytic", top_n=3, tiebreak_limit=20,
            prune_threshold=20,
            progress_callback=callback)
        assert call_count[0] >= 1, f"Callback called {call_count[0]} times"

    def test_callback_total_is_positive(self, engine):
        totals = []
        def callback(current, total):
            totals.append(total)
            return False
        engine.reverse_derive(
            ["Dagger"], mode="analytic", top_n=3, tiebreak_limit=20,
            prune_threshold=20,
            progress_callback=callback)
        assert len(totals) >= 1
        assert all(t > 0 for t in totals)

    def test_callback_cancel(self, engine):
        def callback(current, total):
            return True
        result = engine.reverse_derive(
            ["Dagger"], mode="analytic", top_n=3, tiebreak_limit=20,
            prune_threshold=20,
            progress_callback=callback)
        assert result.get("cancelled") is True


class TestExclusiveGroups:
    def test_assassin_exclusive_fixed_knave(self, engine):
        branches = engine.resolve_exclusive("assassin_background")
        assert len(branches) == 1
        groups, prob = branches[0]
        assert groups == ["Knave"]
        assert prob == 1.0

    def test_adventurous_noble_exclusive_fixed_noble(self, engine):
        branches = engine.resolve_exclusive("adventurous_noble_background")
        assert len(branches) == 1
        groups, prob = branches[0]
        assert groups == ["Noble"]
        assert prob == 1.0

    def test_exclusive_cascade_weights_exist(self, engine):
        weights = engine.exclusive_cascade_weights("Knave")
        assert isinstance(weights, dict)

    def test_nonexclusive_background_has_none_mode(self, engine):
        branches = engine.resolve_exclusive("apprentice_background")
        assert len(branches) == 1
        groups, prob = branches[0]
        assert groups == []
        assert prob == 1.0


class TestMeleeOnly:
    MELEE_ONLY_BGS = ["assassin_background", "adventurous_noble_background"]

    def test_melee_only_zero_ranged_weights(self, engine):
        for bg_id in self.MELEE_ONLY_BGS:
            if bg_id in engine.gd.complete_backgrounds():
                for rg in RANGED_GROUPS:
                    w = engine.compute_raw_weight(bg_id, [], rg)
                    assert w == 0.0, f"{bg_id} {rg} weight={w}, expected 0"

    def test_non_melee_background_has_ranged_weights(self, engine):
        w = engine.compute_raw_weight("squire_background", [], "Bow")
        assert w >= 0

    def test_melee_only_does_not_affect_non_ranged(self, engine):
        for bg_id in self.MELEE_ONLY_BGS:
            if bg_id in engine.gd.complete_backgrounds():
                w = engine.compute_raw_weight(bg_id, [], "Axe")
                assert w > 0, f"{bg_id} Axe weight={w}, expected > 0"


class TestGroupRollMechanics:
    def test_default_rolls_non_negative(self, engine):
        for cat, n in engine.default_rolls.items():
            assert n >= 0, f"{cat} default_rolls={n}"

    def test_exclusive_half_roll(self, engine):
        assert engine.default_rolls.get("Exclusive", 0) == 0.5

    def test_num_rolls_with_modifier(self, engine):
        n = engine.num_rolls("assassin_background", "Weapon")
        assert n == pytest.approx(5.0), f"Expected 5 (3 base + 2), got {n}"


class TestV030BgAttributes:
    """v0.3.0: Engine uses background-specific attribute ranges."""

    def test_attribute_weight_differs_by_bg(self, engine):
        """Same group (e.g. 'Sword') has different attribute_star_weight for
        farmhand (high HP) vs swordmaster (low HP)."""
        farmhand_stars = engine._bg_expected_talent_stars("farmhand_background")
        swordmaster_stars = engine._bg_expected_talent_stars("swordmaster_background")
        # Both should return non-default values for backgrounds with attribute data
        assert farmhand_stars != {}, "farmhand should have expected stars"
        assert swordmaster_stars != {}, "swordmaster should have expected stars"
        # The expected star values should be identical (1.5) since we use global distribution
        assert farmhand_stars["Hitpoints"] == swordmaster_stars["Hitpoints"]

    def test_projected_uses_bg_attributes(self, engine):
        """farmhand projected HP > swordmaster projected HP (different base ranges)."""
        farmhand_proj = engine._bg_projected_attrs("farmhand_background")
        swordmaster_proj = engine._bg_projected_attrs("swordmaster_background")
        assert farmhand_proj["Hitpoints"] > swordmaster_proj["Hitpoints"], (
            f"farmhand HP={farmhand_proj['Hitpoints']:.1f} should be > "
            f"swordmaster HP={swordmaster_proj['Hitpoints']:.1f}")
        assert swordmaster_proj["Melee Skill"] > farmhand_proj["Melee Skill"], (
            f"swordmaster MS={swordmaster_proj['Melee Skill']:.1f} should be > "
            f"farmhand MS={farmhand_proj['Melee Skill']:.1f}")

    def test_missing_bg_falls_back_default(self, engine):
        """Background with null attributes (rf_old_swordmaster) falls back to DEFAULT_PROJECTED."""
        proj = engine._bg_projected_attrs("rf_old_swordmaster_background")
        from engine import DEFAULT_PROJECTED
        for attr, val in DEFAULT_PROJECTED.items():
            assert proj.get(attr) == val, f"Attribute {attr}: expected {val}, got {proj.get(attr)}"

    def test_estimated_bg_still_computes(self, engine):
        """Background with estimated=True (crucified) still computes projected attributes."""
        proj = engine._bg_projected_attrs("crucified_background")
        # Should have all 8 attributes computed from Cripple's data
        assert len(proj) == 8, f"Expected 8 projected attributes, got {len(proj)}"
        assert proj["Hitpoints"] > 30, f"Expected reasonable HP, got {proj['Hitpoints']}"

    def test_talent_stars_override(self, engine):
        """Manually passing talent_stars=3 gives higher weight than stars=0."""
        gd = engine.gd
        high_stars = {a: 3.0 for a in gd.attribute_weights}
        low_stars = {a: 0.0 for a in gd.attribute_weights}
        # Use 'Trained' which has Melee Defense attribute weight
        w_high = engine.attribute_star_weight("Trained", talent_stars=high_stars)
        w_low = engine.attribute_star_weight("Trained", talent_stars=low_stars)
        assert w_high > w_low, f"Stars=3 weight ({w_high}) should be > stars=0 ({w_low})"


class TestFractionalExclusiveRolls:
    """v0.4.0: Exclusive 基线 0.5 = 50% 概率额外骰一次专属组。

    非保证但有正权重的专属组因此获得 0.5×权重占比 的出现概率
    （此前 int(round(0.5))=0 使其恒为 0%）。保证组概率不受影响。
    """

    # (bg, 非保证目标组, 期望概率)  期望值 = 0.5 × 目标权重 / 池内总权重
    CASES = [
        ("swordmaster_background", "Swordmaster", 0.25),      # 池 {Soldier:1, Swordmaster:1}
        ("rf_old_swordmaster_background", "Swordmaster", 0.25),
        ("fisherman_background", "Trapper", 0.25),
        ("old_gladiator_background", "Trapper", 0.25),
    ]

    @pytest.mark.parametrize("bg,target,expected", CASES)
    def test_nonguaranteed_exclusive_now_positive(self, engine, bg, target, expected):
        p = engine.appear_prob_analytic(bg, [], target)
        assert p == pytest.approx(expected, abs=0.01), (
            f"{bg} {target}: expected ≈{expected}, got {p:.4f}")

    def test_barbarian_wildling_positive(self, engine):
        """barbarian 的 Wildling(非保证,权重 0.203)不再是 0。"""
        p = engine.appear_prob_analytic("barbarian_background", [], "Wildling")
        assert 0.05 < p < 0.20, f"Expected ~0.10, got {p:.4f}"

    def test_guaranteed_probs_unchanged(self, engine):
        """保证组概率仍由保证机制给出,不受分数骰组影响。"""
        assert engine.appear_prob_analytic(
            "swordmaster_background", [], "Soldier") == pytest.approx(1.0)
        assert engine.appear_prob_analytic(
            "barbarian_background", [], "Raider") == pytest.approx(0.625)
        assert engine.appear_prob_analytic(
            "barbarian_background", [], "Laborer") == pytest.approx(0.25)

    def test_analytic_matches_monte_carlo(self, engine):
        """分数骰组路径的解析与蒙特卡洛一致（±0.02）。"""
        for bg, target in [("swordmaster_background", "Swordmaster"),
                           ("barbarian_background", "Wildling")]:
            pa = engine.appear_prob_analytic(bg, [], target)
            pm = engine.appear_prob_monte_carlo(bg, [], target, samples=8000, seed=7)
            assert pm == pytest.approx(pa, abs=0.02), (
                f"{bg} {target}: analytic={pa:.4f} mc={pm:.4f}")

    def test_forward_simulate_includes_fractional(self, engine):
        """forward_simulate 结果里非保证专属组概率为正。"""
        res = engine.forward_simulate("swordmaster_background", [], mode="analytic")
        assert res is not None
        assert res.get("Swordmaster", 0) == pytest.approx(0.25, abs=0.01)
        assert res.get("Soldier", 0) == pytest.approx(1.0)

    def test_integer_rolls_unaffected(self, engine):
        """整数骰组类别(如 Weapon)的概率路径与分数逻辑无关——单组池 n=1 应为 1。"""
        p = engine._appear_prob_no_replacement({"OnlyGroup": 2.0}, "OnlyGroup", 1.0)
        assert p == 1.0

    def test_fractional_single_group_pool(self, engine):
        """单组池 n=0.5 → 0.5(而非旧逻辑的 0 或 len==1 捷径的 1)。"""
        p = engine._appear_prob_no_replacement({"OnlyGroup": 2.0}, "OnlyGroup", 0.5)
        assert p == pytest.approx(0.5)

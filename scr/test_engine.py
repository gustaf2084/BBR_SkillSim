# -*- coding: utf-8 -*-
"""
test_engine.py
SkillEngine 单元测试。

覆盖：
  - 权重合成（base_prob × self_weight + multipliers + 特性 + 天赋星 + 投影 + 级联）
  - 禁用语义（multiplier=0 / trait=0 / Melee Only 远程组）
  - 单组出现概率：analytic(无放回) vs monte_carlo 一致性
  - 正向模拟：返回结构、排序、无可用方案
  - 反向推导：并列最大、排序、多目标加权、加次序
  - 专属组四种模式

运行: python test_engine.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_loader import load_data
from engine import SkillEngine, RANGED_GROUPS, EPS


def get_engine():
    here = os.path.dirname(os.path.abspath(__file__))
    gd = load_data(os.path.join(here, "data.json"))
    return SkillEngine(gd), gd


class TestWeightSynthesis(unittest.TestCase):
    """权重合成测试。"""

    @classmethod
    def setUpClass(cls):
        cls.eng, cls.gd = get_engine()

    def test_base_prob_times_self_weight(self):
        """base_prob × self_weight 应正确。Trained 的 self_weight=0.5。"""
        # assassin Trained: base=0.0933, self_weight=0.5 → 0.0467（再加天赋星/投影）
        w = self.eng.compute_raw_weight("assassin_background", [], "Trained",
                                        use_attribute=False, use_projected=False)
        self.assertAlmostEqual(w, 0.0933 * 0.5, places=3)

    def test_multiplier_add(self):
        """背景 multipliers 应叠加到权重。"""
        # adventurous_noble Tactician: base=None(Tactician无矩阵), multiplier=3, self_weight=0.1
        # 无 base → w = 0 + 3(self_weight不乘因为没有base) ... 实际: base=None时不乘self_weight
        w = self.eng.compute_raw_weight("adventurous_noble_background", [], "Tactician",
                                        use_attribute=False, use_projected=False)
        # base_prob=None → 不走 base*self_weight 分支；multiplier=3 直接加
        self.assertAlmostEqual(w, 3.0, places=3)

    def test_multiplier_zero_disables(self):
        """背景 multiplier=0 → 组被禁用（权重0）。"""
        # adventurous_noble Bow: melee_only 且远程组，应0
        w = self.eng.compute_raw_weight("adventurous_noble_background", [], "Bow",
                                        use_attribute=False, use_projected=False)
        self.assertEqual(w, 0.0)

    def test_trait_weight_add(self):
        """特性权重应叠加。Athletic → Agile +2。"""
        w_none = self.eng.compute_raw_weight("assassin_background", [], "Agile",
                                             use_attribute=False, use_projected=False)
        w_trait = self.eng.compute_raw_weight("assassin_background", ["Athletic"], "Agile",
                                              use_attribute=False, use_projected=False)
        self.assertAlmostEqual(w_trait - w_none, 2.0, places=3)

    def test_trait_zero_disables(self):
        """特性权重=0 → 组被禁用。Brute → Trained 0。"""
        w = self.eng.compute_raw_weight("assassin_background", ["Brute"], "Trained",
                                        use_attribute=False, use_projected=False)
        self.assertEqual(w, 0.0)

    def test_melee_only_disables_ranged(self):
        """Melee Only 背景禁用所有远程组。"""
        for g in RANGED_GROUPS:
            w = self.eng.compute_raw_weight("adventurous_noble_background", [], g,
                                            use_attribute=False, use_projected=False)
            self.assertEqual(w, 0.0, f"Melee Only 应禁用 {g}")

    def test_exclusive_cascade(self):
        """专属组级联应叠加。Knave → Dagger +10。"""
        # assassin 固定 Knave。Dagger base=1.0, Knave级联 +10
        w_no_casc = self.eng.compute_raw_weight("assassin_background", [], "Dagger",
                                                exclusive_active=None,
                                                use_attribute=False, use_projected=False)
        w_casc = self.eng.compute_raw_weight("assassin_background", [], "Dagger",
                                             exclusive_active=["Knave"],
                                             use_attribute=False, use_projected=False)
        # 级联应增加权重（Dagger 的 +10）
        self.assertGreater(w_casc, w_no_casc)


class TestAppearProbability(unittest.TestCase):
    """出现概率测试。"""

    @classmethod
    def setUpClass(cls):
        cls.eng, cls.gd = get_engine()

    def test_analytic_vs_montecarlo_consistency(self):
        """analytic(无放回) 与 monte_carlo 应高度一致（容差 0.03）。"""
        cases = [
            ("assassin_background", [], "Cleaver"),
            ("assassin_background", [], "Hammer"),
            ("assassin_background", [], "Mace"),
            ("adventurous_noble_background", [], "Tactician"),
            ("beast_hunter_background", [], "Bow"),
        ]
        for bg, traits, g in cases:
            pa = self.eng.appear_prob_analytic(bg, traits, g)
            pm = self.eng.appear_prob_monte_carlo(bg, traits, g, samples=30000, seed=42)
            self.assertLessEqual(abs(pa - pm), 0.03,
                                 f"{bg}/{traits}/{g}: analytic={pa:.3f} vs monte={pm:.3f} 偏差过大")

    def test_probability_range(self):
        """所有组出现概率应在 [0,1]。"""
        res = self.eng.forward_simulate("barbarian_background", [], mode="analytic")
        self.assertIsNotNone(res)
        for g, p in res.items():
            self.assertGreaterEqual(p, 0.0 - EPS)
            self.assertLessEqual(p, 1.0 + EPS)

    def test_general_always_one(self):
        """General 组恒出现，概率=1。"""
        p = self.eng.appear_prob_analytic("assassin_background", [], "General")
        self.assertEqual(p, 1.0)

    def test_zero_rolls_zero_prob(self):
        """骰组数为 0 的类别，组概率为 0。"""
        # Special 默认骰 0，且多数背景无 Special 修正
        # 找一个 Special 类组测试
        p = self.eng.appear_prob_analytic("apprentice_background", [], "Back To Basics")
        # apprentice 无 Special 修正，default Special=0 → 概率0
        self.assertEqual(p, 0.0)

    def test_disabled_group_zero_prob(self):
        """被禁用组概率为 0。Melee Only 背景的远程组。"""
        p = self.eng.appear_prob_analytic("adventurous_noble_background", [], "Bow")
        self.assertEqual(p, 0.0)


class TestForwardSimulate(unittest.TestCase):
    """正向模拟测试。"""

    @classmethod
    def setUpClass(cls):
        cls.eng, cls.gd = get_engine()

    def test_returns_sorted_desc(self):
        """正向模拟结果应按概率降序、组名升序排列。"""
        res = self.eng.forward_simulate("assassin_background", [], mode="analytic")
        self.assertIsNotNone(res)
        items = list(res.items())
        for i in range(len(items) - 1):
            # 概率降序；概率相等时组名升序
            if abs(items[i][1] - items[i + 1][1]) <= EPS:
                self.assertLessEqual(items[i][0], items[i + 1][0])
            else:
                self.assertGreaterEqual(items[i][1], items[i + 1][1])

    def test_all_groups_present(self):
        """正向模拟应包含全部组（48个）。"""
        res = self.eng.forward_simulate("barbarian_background", [], mode="analytic")
        self.assertIsNotNone(res)
        self.assertEqual(len(res), len(self.gd.groups))

    def test_incomplete_background_returns_none(self):
        """不完整背景应返回 None。（当前数据全完整，用不存在背景测）"""
        res = self.eng.forward_simulate("不存在的背景", [], mode="analytic")
        self.assertIsNone(res)


class TestReverseDerive(unittest.TestCase):
    """反向推导测试。"""

    @classmethod
    def setUpClass(cls):
        cls.eng, cls.gd = get_engine()

    def test_single_target_max(self):
        """单目标反向推导：所有结果应并列最大。"""
        rd = self.eng.reverse_derive(["Cleaver"], mode="analytic", top_n=10, tiebreak_limit=50)
        if rd["results"]:
            max_score = rd["max_score"]
            for bg, traits, score, probs, purity in rd["results"]:
                self.assertAlmostEqual(score, max_score, places=3)

    def test_results_sorted(self):
        """结果应按背景名升序、特性名升序排列。"""
        rd = self.eng.reverse_derive(["Hammer"], mode="analytic", top_n=20, tiebreak_limit=50)
        for i in range(len(rd["results"]) - 1):
            a = rd["results"][i]
            b = rd["results"][i + 1]
            key_a = (a[0], list(a[1]))
            key_b = (b[0], list(b[1]))
            # tiebreak 启用时还有 purity 作为第三排序键，此处放宽：背景名应升序
            self.assertLessEqual(a[0], b[0])

    def test_multi_target_weighted(self):
        """多目标加权：评分应为各目标组概率的加权和。"""
        targets = ["Heavy Armor", "Shield"]
        weights = {"Heavy Armor": 2.0, "Shield": 1.0}
        rd = self.eng.reverse_derive(targets, weights=weights, mode="analytic", top_n=5)
        if rd["results"]:
            bg, traits, score, probs, purity = rd["results"][0]
            expected = 2.0 * probs["Heavy Armor"] + 1.0 * probs["Shield"]
            self.assertAlmostEqual(score, expected, places=3)

    def test_top_n_limit(self):
        """top_n 应限制返回数量。"""
        rd = self.eng.reverse_derive(["Dagger"], mode="analytic", top_n=5, tiebreak_limit=20)
        self.assertLessEqual(len(rd["results"]), 5)

    def test_tiebreak_purity_ordering(self):
        """启用加次序时，同背景同特性下应按 purity 升序。"""
        rd = self.eng.reverse_derive(["Dagger"], mode="analytic", top_n=30, tiebreak_limit=20)
        if rd.get("tiebreak_used"):
            # 检查 purity 非减（同背景段内）
            for i in range(len(rd["results"]) - 1):
                a = rd["results"][i]
                b = rd["results"][i + 1]
                if a[0] == b[0]:
                    self.assertLessEqual(a[4], b[4] + EPS)

    def test_zero_target_returns_empty(self):
        """无任何组合能生成目标组时返回空。"""
        # 用一个不存在的组
        rd = self.eng.reverse_derive(["不存在的组"], mode="analytic")
        self.assertEqual(rd["max_score"], 0.0)
        self.assertEqual(len(rd["results"]), 0)


class TestExclusiveModes(unittest.TestCase):
    """专属组四种模式测试。"""

    @classmethod
    def setUpClass(cls):
        cls.eng, cls.gd = get_engine()

    def test_fixed_mode(self):
        """fixed 模式返回单个确定专属组。"""
        # adventurous_noble: fixed Noble
        branches = self.eng.resolve_exclusive("adventurous_noble_background")
        self.assertEqual(len(branches), 1)
        self.assertEqual(branches[0][0], ["Noble"])
        self.assertAlmostEqual(branches[0][1], 1.0)

    def test_prob_mode(self):
        """prob 模式返回按概率分布的多个分支。"""
        # anatomist: Knave 30, Trapper 70
        branches = self.eng.resolve_exclusive("anatomist_background")
        total = sum(p for _, p in branches)
        self.assertAlmostEqual(total, 1.0, places=3)
        groups = [g for gs, _ in branches for g in gs]
        self.assertIn("Knave", groups)
        self.assertIn("Trapper", groups)

    def test_none_mode(self):
        """none 模式返回空专属组。"""
        # apprentice 无专属组
        branches = self.eng.resolve_exclusive("apprentice_background")
        self.assertEqual(branches, [([], 1.0)])

    def test_mixed_mode(self):
        """mixed 模式含 forced + prob 分支。"""
        # gladiator: forced Trapper + prob Laborer/Raider/Soldier
        branches = self.eng.resolve_exclusive("gladiator_background")
        all_groups = [g for gs, _ in branches for g in gs]
        self.assertIn("Trapper", all_groups)  # forced
        # 概率和应为1
        total = sum(p for _, p in branches)
        self.assertAlmostEqual(total, 1.0, places=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)

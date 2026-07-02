# -*- coding: utf-8 -*-
"""
engine.py
《战场兄弟·重铸》技能树模拟器的概率计算引擎。

核心概念：
  - 技能树组（Perk Group）按 6 类别顺序骰出：Shared → Exclusive → Weapon → Armor → Fighting Style → Special
  - 每个类别骰 n 组（n = 默认骰组基线 + 背景修正），组内在合成权重上做加权随机抽样
  - 「单组出现概率」= 给定背景+特性下，该组在最终生成树中至少被骰出一次的概率

权重合成（合成权重 W）:
  W(g) = base_prob(B,g) * self_weight(g)        # 基础概率 × 组自身系数
       + background_multiplier(B,g)             # 背景 multipliers 加成
       + Σ trait_weight(t,g)                    # 特性权重
       + attribute_star_weight(g)               # 天赋星修正（默认中值）
       + projected_attr_weight(g)               # 投影属性修正（默认中值）
       + Σ exclusive_cascade(E,g)               # 已骰专属组 E 的级联修正
  规则：
    - 任一来源使 g 权重为 0 → 该组不出现
    - Melee Only 背景 → 远程组（Bow/Crossbow/Throwing/Ranged）权重强制 0
    - Tactician 无 base_prob（null）→ 仅靠权重规则合成

两种计算模式：
  - analytic（解析近似）：类别内按合成权重归一，P(出现)=1-(1-p)^n
  - monte_carlo（蒙特卡洛）：固定种子大量抽样统计经验概率

公开 API:
  class SkillEngine:
    forward_simulate(bg_id, trait_ids, ...) -> {group: prob} 或 None（无可用方案）
    reverse_derive(target_groups, weights, ...) -> [(bg, trait组合, prob), ...]
    cascade_weights_for_exclusive(...) -> {group: weight}
"""

from __future__ import annotations

import random
from collections import OrderedDict
from collections.abc import Callable
from typing import Any

from data_loader import GameData

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

CATEGORY_ORDER = ["Shared", "Exclusive", "Weapon", "Armor", "Fighting Style", "Special"]

RANGED_GROUPS = {"Bow", "Crossbow", "Throwing", "Ranged"}

EPS = 1e-9

# 默认天赋星中值（每属性取 1 颗星作为默认，影响 attribute_weights 的乘子）
DEFAULT_TALENT_STARS = 1.0

# 默认投影属性中值（11 级时各属性取背景无关的中位数近似）
# 用于 projected_attributes 的 step 计算；超过 cutoff 才加权。
DEFAULT_PROJECTED = {
    "Melee Skill": 65.0,
    "Ranged Skill": 65.0,
    "Melee Defense": 15.0,
    "Ranged Defense": 5.0,
    "Hitpoints": 70.0,
    "Fatigue": 110.0,
    "Initiative": 110.0,
    "Bravery": 45.0,
}


# ---------------------------------------------------------------------------
# 引擎
# ---------------------------------------------------------------------------

# Type aliases for readability
GroupId = str
BgId = str
TraitId = str
WeightDict = dict[str, float]
Background = dict[str, Any]
Trait = dict[str, Any]
GroupDef = dict[str, Any]
ReverseResultItem = tuple[str, tuple[str, ...], float, dict[str, float], float]
ReverseResult = dict[str, Any]


class SkillEngine:
    """技能树出现概率计算引擎。"""

    gd: GameData
    big_weight: float
    default_rolls: dict[str, float]
    _groups_by_cat: dict[str, list[str]]
    _all_groups: list[str]
    _forward_cache: dict[tuple, OrderedDict | None]
    _forward_cache_max: int
    _norepl_cache: dict[str, dict[tuple[int, int], float]]

    def __init__(self, game_data: GameData) -> None:
        """
        参数:
          game_data: GameData 实例（来自 data_loader.load_data）
        """
        self.gd = game_data
        self.big_weight: float = game_data.big_weight
        self.default_rolls: dict[str, float] = game_data.default_group_rolls
        # 预计算各类别组列表
        self._groups_by_cat: dict[str, list[str]] = {}
        for cat in CATEGORY_ORDER:
            self._groups_by_cat[cat] = game_data.groups_by_category(cat)
        self._all_groups: list[str] = list(game_data.groups.keys())
        # 缓存层
        self._forward_cache: dict[tuple, OrderedDict | None] = {}     # key -> OrderedDict | None (analytic only)
        self._forward_cache_max: int = 200
        self._norepl_cache: dict[str, dict[tuple[int, int], float]] = {}      # target: {bitmask_state: result}  for _appear_prob_no_replacement

    # ------------------------------------------------------------------
    # 权重合成
    # ------------------------------------------------------------------

    def exclusive_cascade_weights(self, exclusive_group_name: str) -> dict[str, float]:
        """返回某专属组的级联权重修正 {group: weight}。"""
        ec: dict[str, Any] = self.gd.exclusive_groups.get(exclusive_group_name, {})
        return dict(ec.get("other_weights", {}))

    def attribute_star_weight(self, group: str, talent_stars: dict[str, float] | None = None) -> float:
        """
        天赋星对组权重的修正。
        talent_stars: {attribute: stars} 或 None（用默认中值）。
        """
        if talent_stars is None:
            talent_stars = {a: DEFAULT_TALENT_STARS for a in self.gd.attribute_weights}
        w: float = 0.0
        for attr, stars in talent_stars.items():
            attr_map: dict[str, Any] = self.gd.attribute_weights.get(attr, {})
            if group in attr_map:
                multiplier: float = attr_map[group]
                if multiplier > 0:
                    w += multiplier * stars
        return w

    def projected_attr_weight(self, group: str, projected: dict[str, float] | None = None) -> float:
        """
        投影属性对组权重的修正。
        projected: {attribute: value} 或 None（用默认中值）。
        规则: 若投影值超过 cutoff，权重 += base * (value - cutoff) 的某种近似。
        简化为: base * max(0, (value - cutoff) / 10) 作为加成（保守估计）。
        """
        proj: dict[str, Any] | None = self.gd.projected_attributes.get(group)
        if not proj:
            return 0.0
        if projected is None:
            projected = DEFAULT_PROJECTED
        base: float = proj.get("base", 0.0)
        cutoff: float | None = proj.get("cutoff")
        if cutoff is None:
            # 无 cutoff 的组（如 Dagger/Shield 投影），用 base 作为基础权重
            return base
        # 找该组 governed by 的属性（按组名推断）
        gov_attr: str = self._group_governing_attr(group)
        val: float = projected.get(gov_attr, 0.0)
        if val > cutoff:
            # 每超过 cutoff 10 点加一个 base 的权重
            return base * max(0.0, (val - cutoff) / 10.0)
        return 0.0

    def _group_governing_attr(self, group: str) -> str:
        """根据组名推断投影属性受哪个属性管辖。"""
        # 武器组受 Melee Skill 管辖（远程武器受 Ranged Skill）
        if group in {"Bow", "Crossbow", "Throwing", "Ranged"}:
            return "Ranged Skill"
        if group == "Shield":
            return "Melee Defense"
        if group == "Fencer":
            return "Initiative"
        return "Melee Skill"

    # ── v0.3.0: Background-specific attribute & projected computation ──

    def _bg_expected_talent_stars(self, bg_id: str) -> dict[str, float]:
        """Compute per-attribute expected talent stars from the background's
        attribute ranges and the global star distribution (60/30/10).

        Backgrounds with no attribute data fall back to DEFAULT_TALENT_STARS
        (1.0 star) for all attributes. Backgrounds with attribute data use the
        weighted expectation: 0.6*1 + 0.3*2 + 0.1*3 = 1.5.

        Excluded attributes (talent_excluded_attributes per bg) return 0.0.
        """
        bg = self.gd.backgrounds.get(bg_id)
        if not bg or not bg.get("attributes"):
            return {a: DEFAULT_TALENT_STARS for a in self.gd.attribute_weights}
        dist = self.gd.talent_star_distribution()
        expected = sum(int(s) * p for s, p in dist.items())  # ≈ 1.5
        excluded = self.gd.talent_excluded_attributes().get(bg_id, [])
        return {a: (0.0 if a in excluded else expected)
                for a in self.gd.attribute_weights}

    def _bg_projected_attrs(self, bg_id: str,
                            talent_stars: dict[str, float] | None = None
                            ) -> dict[str, float]:
        """Compute projected level-11 attributes from the background's starting
        attribute ranges and talent star estimates.

        Uses the background's min-max midpoint as base, then adds 10 level-ups
        worth of per-level gains computed from the talent_levelup_ranges table,
        linearly interpolated by star count.

        Backgrounds with no attribute data fall back to DEFAULT_PROJECTED.
        """
        bg = self.gd.backgrounds.get(bg_id)
        attrs = bg.get("attributes") if bg else None
        if not attrs:
            return dict(DEFAULT_PROJECTED)
        if talent_stars is None:
            talent_stars = self._bg_expected_talent_stars(bg_id)
        lv_ranges = self.gd.talent_levelup_ranges()
        max_lv = self.gd.max_level  # 11
        projected: dict[str, float] = {}
        for attr, (mn, mx) in attrs.items():
            base = (mn + mx) / 2.0
            stars = talent_stars.get(attr, 1.0)
            lr = lv_ranges.get(attr, {})
            range_low = lr.get("0", [1, 3])
            range_high = lr.get("3", [3, 4])
            avg_low = (range_low[0] + range_low[1]) / 2.0
            avg_high = (range_high[0] + range_high[1]) / 2.0
            per_star = (avg_high - avg_low) / 3.0
            per_level = avg_low + stars * per_star
            total_gain = per_level * (max_lv - 1)  # 10 level-ups
            projected[attr] = base + total_gain
        return projected

    def compute_raw_weight(self, bg_id: str, trait_ids: list[str], group: str,
                           exclusive_active: list[str] | None = None,
                           use_attribute: bool = True,
                           use_projected: bool = True,
                           talent_stars: dict[str, float] | None = None,
                           projected: dict[str, float] | None = None) -> float:
        """
        计算单个组的合成权重（未归一化）。
        exclusive_active: 当前已骰出的专属组名列表（用于级联）；None 表示不考虑级联。
        use_attribute / use_projected: 是否计入天赋星/投影属性修正。
        talent_stars / projected: 手动覆盖值；None 时自动从背景属性推导。
        返回: float 权重；若组被禁用返回 0.0；若组无任何权重来源返回 0.0。
        """
        gd = self.gd
        bg = gd.backgrounds.get(bg_id)
        if bg is None:
            return 0.0

        gdef = gd.groups.get(group)
        if gdef is None:
            return 0.0

        # Melee Only 禁用远程组
        if bg.get("melee_only") and group in RANGED_GROUPS:
            return 0.0

        # 基础概率
        base_prob = bg.get("base_probabilities", {}).get(group)
        self_w = gdef.get("self_weight")

        w = 0.0
        # 基础概率 × self_weight（self_weight 缺省视为 1.0）
        if base_prob is not None:
            sw = 1.0 if self_w is None else self_w
            # self_weight 为 0 表示该组自身系数为 0（如 Ranged/Professional）
            w += base_prob * sw

        # 背景 multipliers
        mult = bg.get("multipliers", {}).get(group)
        if mult is not None:
            # 0 表示禁用
            if mult == 0.0:
                return 0.0
            w += mult

        # 特性权重
        for tid in trait_ids:
            t = gd.traits.get(tid)
            if t:
                tw = t.get("weights", {}).get(group)
                if tw is not None:
                    if tw == 0.0:
                        return 0.0  # 特性禁用该组
                    w += tw

        # 天赋星
        if use_attribute:
            stars = talent_stars if talent_stars is not None else self._bg_expected_talent_stars(bg_id)
            w += self.attribute_star_weight(group, talent_stars=stars)

        # 投影属性
        if use_projected:
            proj = projected if projected is not None else self._bg_projected_attrs(bg_id)
            w += self.projected_attr_weight(group, projected=proj)

        # 专属组级联
        if exclusive_active:
            for eg in exclusive_active:
                cascade = self.exclusive_cascade_weights(eg)
                cw = cascade.get(group)
                if cw is not None:
                    if cw == 0.0:
                        return 0.0
                    w += cw

        return max(0.0, w)

    # ------------------------------------------------------------------
    # 骰组数量
    # ------------------------------------------------------------------

    def num_rolls(self, bg_id: str, category: str) -> float:
        """某类别骰组数 = 默认基线 + 背景修正，最小 0。"""
        base: float = self.default_rolls.get(category, 0)
        bg: dict[str, Any] = self.gd.backgrounds.get(bg_id, {})
        mod: float = bg.get("group_rolls", {}).get(category, 0)
        n: float = base + mod
        if isinstance(n, float):
            n = n  # Exclusive 基线 0.5 保留浮点
        return max(0.0, n)

    # ------------------------------------------------------------------
    # 专属组确定
    # ------------------------------------------------------------------

    def resolve_exclusive(self, bg_id: str, rng: random.Random | None = None) -> list[tuple[list[str], float]]:
        """
        根据背景的 exclusive 配置，返回可能的专属组结果列表（带概率）。
        返回: [(exclusive_groups_list, probability), ...]
          - fixed: [([group], 1.0)]
          - prob:  [([g1], p1), ([g2], p2), ([], none_chance)]
          - mixed: forced 组必出 + prob 分支
          - none:  [([], 1.0)]
        """
        bg: dict[str, Any] = self.gd.backgrounds.get(bg_id, {})
        exc: dict[str, Any] = bg.get("exclusive", {"mode": "none"})
        mode: str = exc.get("mode", "none")

        if mode == "none":
            return [([], 1.0)]
        if mode == "fixed":
            return [([exc.get("group")], 1.0)]
        if mode == "prob":
            picks: dict[str, float] = exc.get("picks", {})
            none_chance: float = exc.get("none_chance", 0.0)
            total: float = sum(picks.values()) + none_chance
            if total <= 0:
                return [([], 1.0)]
            results: list[tuple[list[str], float]] = []
            for g, p in picks.items():
                results.append(([g], p / total))
            if none_chance > 0:
                results.append(([], none_chance / total))
            return results
        if mode == "mixed":
            forced: list[str] = exc.get("forced", [])
            picks = exc.get("picks", {})
            none_chance = exc.get("none_chance", 0.0)
            total = sum(picks.values()) + none_chance
            results = []
            for g, p in picks.items():
                results.append((forced + [g], p / total if total > 0 else 0))
            if none_chance > 0:
                results.append((forced[:], none_chance / total if total > 0 else 0))
            # 若只有 forced 无 picks
            if not picks and not none_chance and forced:
                results = [(forced[:], 1.0)]
            return results
        return [([], 1.0)]

    def _get_guaranteed_exclusive_probs(self, bg_id: str) -> dict[str, float]:
        """Return {group: guaranteed_prob} for groups guaranteed by exclusive config.

        Covers fixed (100%), prob (weighted), and mixed (forced always 100% +
        picks weighted) modes. Returns empty dict if background has no guaranteed
        exclusive groups.

        IMPORTANT: This "guaranteed" probability OVERRIDES (not adds to) the normal
        "Exclusive category rolls 0.5 times" logic. In the mod, exclusive group
        assignment is a separate guaranteed roll independent of the category-based
        rolling system. The guaranteed probability equals the exclusive branch
        probability directly — no 0.5× roll multiplier applies.
        """
        branches: list[tuple[list[str], float]] = self.resolve_exclusive(bg_id)
        result: dict[str, float] = {}
        for exc_groups, branch_p in branches:
            if branch_p <= 0:
                continue
            for g in exc_groups:
                result[g] = result.get(g, 0.0) + branch_p
        return result

    # ------------------------------------------------------------------
    # 出现概率（解析近似）
    # ------------------------------------------------------------------

    def _appear_prob_no_replacement(self, weights_dict: dict[str, float], target: str, n: float) -> float:
        """
        无放回抽样的解析近似：类别内骰 n 组，计算 target 至少被抽中一次的概率。
        weights_dict: {group: weight}（仅正权重组）
        算法：逐轮计算"本轮未抽中 target"的概率并连乘。
          每轮，target 未被抽中的边际概率 = 1 - w_target/total。
          抽中非 target 组后，该组被移出，剩余权重重新归一。
          由于"抽中哪个非target组"会影响 target 后续权重占比，这里用按权重加权
          的期望更新（对 target 占比做一阶近似），在组数≤12、n≤5 时精度足够。
        使用实例级缓存避免跨调用重复计算。
        """
        if target not in weights_dict or weights_dict[target] <= 0:
            return 0.0
        n_eff: int = int(round(n))
        if n_eff <= 0:
            return 0.0
        if len(weights_dict) == 1:
            return 1.0 if target in weights_dict else 0.0

        # 构建缓存 key：组名列表 + target + n + 权重（避免不同背景的碰撞）
        items: list[tuple[str, float]] = sorted(weights_dict.items(), key=lambda x: x[0])
        names: list[str] = [it[0] for it in items]
        wts: list[float] = [it[1] for it in items]
        target_idx: int = names.index(target) if target in names else -1
        if target_idx < 0:
            return 0.0

        # 实例级记忆化：缓存键包含权重签名以避免不同调用间的碰撞
        cache_key: tuple = (target, tuple((n, round(w, 6)) for n, w in items), n_eff)
        if cache_key in self._norepl_cache:
            return self._norepl_cache[cache_key]

        def p_hit(mask: int, k: int) -> float:
            if k <= 0:
                return 0.0
            # 子结果存储在全局缓存中带前缀
            full_key: tuple = cache_key + (mask, k)
            if full_key in self._norepl_cache:
                return self._norepl_cache[full_key]
            idxs: list[int] = [i for i in range(len(names)) if (mask >> i) & 1]
            if not idxs:
                return 0.0
            total: float = sum(wts[i] for i in idxs)
            if total <= 0:
                return 0.0
            p_target: float = wts[target_idx] / total if (mask >> target_idx) & 1 else 0.0
            p_miss_then_hit: float = 0.0
            for i in idxs:
                if i == target_idx:
                    continue
                pi: float = wts[i] / total
                new_mask: int = mask & ~(1 << i)
                p_miss_then_hit += pi * p_hit(new_mask, k - 1)
            result: float = p_target + p_miss_then_hit
            self._norepl_cache[full_key] = result
            return result

        full_mask: int = (1 << len(names)) - 1
        return p_hit(full_mask, n_eff)

    def appear_prob_analytic(self, bg_id: str, trait_ids: list[str], group: str,
                             use_attribute: bool = True,
                             use_projected: bool = True,
                             talent_stars: dict[str, float] | None = None) -> float:
        """
        解析近似计算单组出现概率（无放回抽样模型，与游戏机制一致）。
        思路:
          - 该组所属类别 C 骰 n 组（无放回）
          - 考虑专属组分支：对每个 exclusive 分支，按级联权重合成该类别内各组权重，
            用无放回解析近似计算 P(target 至少被抽中一次)
          - 多个专属分支按其概率加权求和
        返回: float in [0,1]
        """
        gd = self.gd
        bg: dict[str, Any] | None = gd.backgrounds.get(bg_id)
        if bg is None:
            return 0.0
        gdef: dict[str, Any] | None = gd.groups.get(group)
        if gdef is None:
            return 0.0
        cat: str | None = gdef.get("category")
        if cat == "Always":  # General 恒出现
            return 1.0

        # ── Guaranteed exclusive group: return guarantee probability directly ──
        # The mod resolves exclusive groups via a separate guaranteed mechanism
        # independent of the "Exclusive category 0.5× roll" system.
        # Override the normal category-roll calculation for guaranteed groups.
        if cat == "Exclusive":
            guaranteed: dict[str, float] = self._get_guaranteed_exclusive_probs(bg_id)
            if group in guaranteed:
                return guaranteed[group]

        n: float = self.num_rolls(bg_id, cat)
        if n <= 0:
            return 0.0

        # 专属分支
        branches: list[tuple[list[str], float]] = self.resolve_exclusive(bg_id)
        total_prob: float = 0.0
        for exc_groups, branch_p in branches:
            if branch_p <= 0:
                continue
            # 合成该类别内所有组的权重
            cat_groups: list[str] = self._groups_by_cat.get(cat, [])
            weights: dict[str, float] = {}
            for g in cat_groups:
                w: float = self.compute_raw_weight(
                    bg_id, trait_ids, g,
                    exclusive_active=exc_groups,
                    use_attribute=use_attribute, use_projected=use_projected,
                    talent_stars=talent_stars,
                )
                if w > 0:
                    weights[g] = w
            if not weights:
                p_appear: float = 0.0
            else:
                p_appear = self._appear_prob_no_replacement(weights, group, n)
            total_prob += branch_p * p_appear
        return min(1.0, max(0.0, total_prob))

    # ------------------------------------------------------------------
    # 出现概率（蒙特卡洛）
    # ------------------------------------------------------------------

    def appear_prob_monte_carlo(self, bg_id: str, trait_ids: list[str], group: str,
                                samples: int = 20000, seed: int = 42,
                                use_attribute: bool = True,
                                use_projected: bool = True,
                                talent_stars: dict[str, float] | None = None) -> float:
        """蒙特卡洛模拟单组出现概率。"""
        rng: random.Random = random.Random(seed)
        gd = self.gd
        bg: dict[str, Any] | None = gd.backgrounds.get(bg_id)
        if bg is None:
            return 0.0
        gdef: dict[str, Any] | None = gd.groups.get(group)
        if gdef is None:
            return 0.0
        cat: str | None = gdef.get("category")
        if cat == "Always":
            return 1.0
        n: float = self.num_rolls(bg_id, cat)
        if n <= 0:
            return 0.0
        n_int: int = int(round(n))

        branches: list[tuple[list[str], float]] = self.resolve_exclusive(bg_id)
        # 归一化分支概率
        bp_sum: float = sum(p for _, p in branches)
        if bp_sum <= 0:
            branches = [([], 1.0)]
            bp_sum = 1.0

        hit: int = 0
        cat_groups: list[str] = self._groups_by_cat.get(cat, [])
        for _ in range(samples):
            # 选专属分支
            r: float = rng.random() * bp_sum
            acc: float = 0.0
            chosen_exc: list[str] = []
            for exc_groups, p in branches:
                acc += p
                if r <= acc:
                    chosen_exc = exc_groups
                    break
            # 合成权重
            weights: list[float] = []
            names: list[str] = []
            for g in cat_groups:
                w: float = self.compute_raw_weight(
                    bg_id, trait_ids, g,
                    exclusive_active=chosen_exc,
                    use_attribute=use_attribute, use_projected=use_projected,
                    talent_stars=talent_stars,
                )
                if w > 0:
                    weights.append(w)
                    names.append(g)
            if not weights:
                continue
            # 无放回抽样 n_int 次
            chosen: set[str] = set()
            w_copy: list[float] = list(weights)
            n_copy: list[str] = list(names)
            for _k in range(min(n_int, len(n_copy))):
                if not n_copy:
                    break
                tw: float = sum(w_copy)
                if tw <= 0:
                    break
                rr: float = rng.random() * tw
                a: float = 0.0
                idx: int = 0
                for j, ww in enumerate(w_copy):
                    a += ww
                    if rr <= a:
                        idx = j
                        break
                chosen.add(n_copy[idx])
                n_copy.pop(idx)
                w_copy.pop(idx)
            if group in chosen:
                hit += 1
        return hit / samples

    # ------------------------------------------------------------------
    # 正向模拟
    # ------------------------------------------------------------------

    def forward_simulate(self, bg_id: str, trait_ids: list[str],
                         mode: str = "analytic",
                         use_attribute: bool = True,
                         use_projected: bool = True,
                         samples: int = 20000,
                         seed: int = 42,
                         talent_stars: dict[str, float] | None = None) -> OrderedDict | None:
        """
        正向模拟：给定背景+特性，返回所有组的出现概率分布。
        返回:
          OrderedDict {group: prob}（按概率降序、组名升序），或
          None 表示无可用方案（所有可骰类别都无可用组）。
        analytic 模式使用实例级 LRU 缓存（容量 200）。
        """
        gd = self.gd
        if bg_id not in gd.backgrounds:
            return None
        if bg_id not in gd.complete_backgrounds():
            return None

        # analytic 模式缓存
        cache_key: tuple = ()
        if mode == "analytic":
            cache_key = (bg_id, tuple(sorted(trait_ids)), use_attribute, use_projected,
                         tuple(sorted(talent_stars.items())) if talent_stars else None)
            if cache_key in self._forward_cache:
                return self._forward_cache[cache_key]

        results: dict[str, float] = OrderedDict()
        any_available: bool = False

        # Precompute guaranteed exclusive probabilities.
        # These groups are assigned via a separate mechanism in the mod
        # (independent of the "Exclusive category 0.5× roll" system),
        # so their guaranteed probability OVERRIDES the normal category roll.
        guaranteed_exclusive: dict[str, float] = self._get_guaranteed_exclusive_probs(bg_id)

        for group in self._all_groups:
            gdef: dict[str, Any] = gd.groups.get(group, {})
            cat: str | None = gdef.get("category")
            if cat == "Always":
                results[group] = 1.0
                any_available = True
                continue
            # ── Guaranteed exclusive group: use direct guarantee probability ──
            # Covers fixed (100%), prob (weighted), and mixed modes.
            # The mod resolves exclusive groups via a separate guaranteed mechanism
            # independent of the "Exclusive category 0.5× roll" system.
            # The guarantee probability OVERRIDES the normal category roll.
            if cat == "Exclusive" and group in guaranteed_exclusive:
                p = guaranteed_exclusive[group]
            elif mode == "monte_carlo":
                p: float = self.appear_prob_monte_carlo(
                    bg_id, trait_ids, group, samples=samples, seed=seed,
                    use_attribute=use_attribute, use_projected=use_projected,
                    talent_stars=talent_stars)
            else:
                p = self.appear_prob_analytic(
                    bg_id, trait_ids, group,
                    use_attribute=use_attribute, use_projected=use_projected,
                    talent_stars=talent_stars)
            results[group] = p
            if p > 0:
                any_available = True

        if not any_available:
            if mode == "analytic":
                self._forward_cache[cache_key] = None
            return None

        # 排序：概率降序，组名升序
        sorted_items: list[tuple[str, float]] = sorted(results.items(), key=lambda x: (-x[1], x[0]))
        sorted_results: OrderedDict = OrderedDict(sorted_items)

        if mode == "analytic":
            # LRU 淘汰
            if len(self._forward_cache) >= self._forward_cache_max:
                # 删除最早插入的一个
                oldest: Any = next(iter(self._forward_cache))
                del self._forward_cache[oldest]
            self._forward_cache[cache_key] = sorted_results

        return sorted_results

    def forward_reason_if_none(self, bg_id: str, trait_ids: list[str]) -> str:
        """若正向模拟无可用方案，返回原因说明字符串。"""
        gd = self.gd
        bg: dict[str, Any] = gd.backgrounds.get(bg_id, {})
        reasons: list[str] = []
        # 检查各特性是否禁用了大量组
        for tid in trait_ids:
            t: dict[str, Any] = gd.traits.get(tid, {})
            zeros: list[str] = [g for g, w in t.get("weights", {}).items() if w == 0.0]
            if zeros:
                reasons.append(f"特性「{tid}」禁用了组: {', '.join(zeros)}")
        if bg.get("melee_only"):
            reasons.append("该背景为 Melee Only，远程组被禁用")
        if not reasons:
            reasons.append("所选组合导致所有可骰类别均无可用组")
        return "；".join(reasons)

    # ------------------------------------------------------------------
    # 反向推导
    # ------------------------------------------------------------------

    def reverse_derive(self, target_groups: list[str],
                       weights: dict[str, float] | None = None,
                       mode: str = "analytic",
                       multi_trait: bool = False,
                       max_traits: int = 2,
                       use_attribute: bool = True,
                       use_projected: bool = True,
                       top_n: int | None = None,
                       tiebreak_limit: int = 20,
                       prune_threshold: int = 20,
                       progress_callback: Callable[[int, int], bool | None] | None = None) -> dict[str, Any]:
        """
        反向推导：找出使目标组（们）出现概率最大的背景+特性组合。
        参数:
          target_groups: [group] 目标组列表（单或多）
          weights: {group: score_weight} 各目标组权重（多目标加权评分用）；None 则等权
          mode: analytic / monte_carlo
          multi_trait: False=仅遍历单特性(+无特性)；True=遍历多特性组合
          max_traits: 多特性时最多组合几个
          top_n: 最多返回多少个结果（None=不限）；并列过多时配合 tiebreak 排序取前 N
          tiebreak_limit: 并列结果超过此数时启用"次要组干扰最小"次级排序
          prune_threshold: 两阶段剪枝阈值。>0 时启用剪枝；设为 0 禁用。
          progress_callback: 可选，callable(current, total) — 每完成一个背景调用一次。
            回调返回 True 中断计算（用于取消）。
        返回:
          {
            "max_score": float,
            "tied_count": int,
            "results": [(bg_id, (trait_ids,), score, group_probs, purity), ...]
          }
          或 {"max_score": 0, "results": [], "tied_count": 0}。
        """
        gd = self.gd
        if weights is None:
            weights = {g: 1.0 for g in target_groups}
        bgs: list[str] = gd.complete_backgrounds()
        trait_names: list[str] = sorted(gd.traits.keys())

        # 构造待遍历的特性组合
        if not multi_trait:
            trait_combos: list[list[str]] = [[]] + [[t] for t in trait_names]
        else:
            from itertools import combinations
            trait_combos = [[]]
            for k in range(1, max_traits + 1):
                for combo in combinations(trait_names, k):
                    trait_combos.append(list(combo))

        # ── 两阶段剪枝 ──
        # Ensure prune threshold is at least 2× top_n so the candidate pool
        # is large enough to return top_n distinct backgrounds after dedup.
        effective_prune: int = prune_threshold
        if prune_threshold > 0 and top_n:
            effective_prune = max(prune_threshold, top_n * 2, 20)

        candidate_bgs: list[str] = bgs
        if effective_prune > 0 and len(bgs) > effective_prune:
            # 阶段1: 仅无特性组合，筛选前 prune_threshold 个高分背景
            phase1_scores: list[tuple[str, float]] = []
            for bg_id in bgs:
                group_probs: dict[str, float] = {}
                score: float = 0.0
                for g in target_groups:
                    if mode == "monte_carlo":
                        p: float = self.appear_prob_monte_carlo(
                            bg_id, [], g, use_attribute=use_attribute,
                            use_projected=use_projected)
                    else:
                        p = self.appear_prob_analytic(
                            bg_id, [], g, use_attribute=use_attribute,
                            use_projected=use_projected)
                    group_probs[g] = p
                    score += weights.get(g, 1.0) * p
                if score > 0:
                    phase1_scores.append((bg_id, score))
            phase1_scores.sort(key=lambda x: -x[1])
            candidate_bgs = [bg_id for bg_id, _ in phase1_scores[:effective_prune]]
            if not candidate_bgs:
                return {"max_score": 0.0, "results": [], "tied_count": 0}
            # 阶段2: 仅对高分背景遍历特性组合

        # ── Collect ALL results (not just max-score) ──
        all_results: list[tuple[str, tuple[str, ...], float, dict[str, float]]] = []

        total_bgs: int = len(candidate_bgs)
        for bg_idx, bg_id in enumerate(candidate_bgs):
            # 进度回调 + 取消支持
            if progress_callback is not None:
                should_cancel: bool | None = progress_callback(bg_idx, total_bgs)
                if should_cancel:
                    return {"max_score": 0.0, "results": [], "tied_count": 0,
                            "cancelled": True}
            for combo in trait_combos:
                # 计算各目标组出现概率
                group_probs = {}
                score = 0.0
                for g in target_groups:
                    if mode == "monte_carlo":
                        p = self.appear_prob_monte_carlo(
                            bg_id, combo, g, use_attribute=use_attribute,
                            use_projected=use_projected)
                    else:
                        p = self.appear_prob_analytic(
                            bg_id, combo, g, use_attribute=use_attribute,
                            use_projected=use_projected)
                    group_probs[g] = p
                    score += weights.get(g, 1.0) * p
                if score > 0:
                    all_results.append((bg_id, tuple(combo), score, group_probs))

        if not all_results:
            return {"max_score": 0.0, "results": [], "tied_count": 0}

        # ── Dedup: for each bg_id, keep only the highest-scoring row ──
        # When multi_trait is enabled, the same background may appear with
        # multiple trait combos; keep only the best-scoring one.
        # If same score, prefer lexicographically smaller trait combo.
        deduped: dict[str, tuple[str, tuple[str, ...], float, dict[str, float]]] = {}
        for bg_id, combo, score, group_probs in all_results:
            if bg_id not in deduped or score > deduped[bg_id][2] + EPS:
                deduped[bg_id] = (bg_id, combo, score, group_probs)
            elif abs(score - deduped[bg_id][2]) <= EPS:
                existing_combo: tuple[str, ...] = deduped[bg_id][1]
                if list(combo) < list(existing_combo):
                    deduped[bg_id] = (bg_id, combo, score, group_probs)

        # ── Sort by score descending ──
        deduped_list: list[tuple[str, tuple[str, ...], float, dict[str, float]]] = sorted(
            deduped.values(), key=lambda x: -x[2])

        best_score: float = deduped_list[0][2] if deduped_list else 0.0

        # ── tied_count: how many rows tie with the max score (for summary) ──
        tied_count: int = sum(
            1 for _, _, s, _ in deduped_list if abs(s - best_score) <= EPS)

        # 并列过多时，计算"次要组干扰分"(purity) 用于次级排序
        # purity = 该组合下非目标组的出现概率总和（越小越纯粹，越靠前）
        use_tiebreak: bool = len(deduped_list) > tiebreak_limit
        scored: list[tuple[str, tuple[str, ...], float, dict[str, float], float]] = []
        for bg_id, combo, score, group_probs in deduped_list:
            purity: float = 0.0
            if use_tiebreak:
                # 计算非目标组的总出现概率
                for g in self._all_groups:
                    if g in target_groups:
                        continue
                    gdef: dict[str, Any] = gd.groups.get(g, {})
                    if gdef.get("category") == "Always":
                        continue
                    if mode == "monte_carlo":
                        p = self.appear_prob_monte_carlo(
                            bg_id, list(combo), g, use_attribute=use_attribute,
                            use_projected=use_projected)
                    else:
                        p = self.appear_prob_analytic(
                            bg_id, list(combo), g, use_attribute=use_attribute,
                            use_projected=use_projected)
                    purity += p
            scored.append((bg_id, combo, score, group_probs, purity))

        # 排序：得分降序，同分时干扰分升序（purity 小=更纯粹=更靠前）
        scored.sort(key=lambda x: (-x[2], x[4]))
        if top_n is not None:
            scored = scored[:top_n]
        return {
            "max_score": best_score,
            "tied_count": tied_count,
            "results": scored,
            "tiebreak_used": use_tiebreak,
        }

    # ------------------------------------------------------------------
    # 综合得分（多目标加权，单目标即该组概率）
    # ------------------------------------------------------------------

    def score_combination(self, bg_id: str, trait_ids: list[str],
                          target_groups: list[str],
                          weights: dict[str, float] | None = None,
                          mode: str = "analytic",
                          use_attribute: bool = True,
                          use_projected: bool = True) -> tuple[float, dict[str, float]]:
        """计算某背景+特性组合对目标组集合的加权得分。"""
        if weights is None:
            weights = {g: 1.0 for g in target_groups}
        score: float = 0.0
        probs: dict[str, float] = {}
        for g in target_groups:
            if mode == "monte_carlo":
                p: float = self.appear_prob_monte_carlo(bg_id, trait_ids, g,
                                                         use_attribute=use_attribute,
                                                         use_projected=use_projected)
            else:
                p = self.appear_prob_analytic(bg_id, trait_ids, g,
                                              use_attribute=use_attribute,
                                              use_projected=use_projected)
            probs[g] = p
            score += weights.get(g, 1.0) * p
        return score, probs


# ---------------------------------------------------------------------------
# 自测
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    import os

    from data_loader import load_data
    here = os.path.dirname(os.path.abspath(__file__))
    gd = load_data(os.path.join(here, "data.json"))
    eng = SkillEngine(gd)

    print("=== Self-test 1: adventurous_noble + [] forward (analytic) ===")
    res = eng.forward_simulate("adventurous_noble_background", [], mode="analytic")
    if res:
        for g, p in list(res.items())[:12]:
            print(f"  {g:20} {p:.3f}")
        print(f"  ... {len(res)} groups")
    else:
        print("  No valid build")

    print()
    print("=== Self-test 2: analytic vs monte_carlo (assassin, []) ===")
    for g in ["Dagger", "Light Armor", "Cleaver", "Hammer", "Mace", "Axe", "Sword"]:
        pa = eng.appear_prob_analytic("assassin_background", [], g)
        pm = eng.appear_prob_monte_carlo("assassin_background", [], g, samples=30000, seed=42)
        print(f"  {g:14} analytic={pa:.3f}  monte={pm:.3f}  diff={abs(pa-pm):.3f}")

    print()
    print("=== Self-test 3: reverse derive Dagger (pruning) ===")
    rd = eng.reverse_derive(["Dagger"], mode="analytic", top_n=10, tiebreak_limit=20, prune_threshold=20,
                             progress_callback=lambda c, t: print(f"  Progress: {c+1}/{t}", flush=True) or False)
    print(f"  max_score={rd['max_score']:.3f}, tied={rd['tied_count']}, tiebreak={rd.get('tiebreak_used')}")
    for bg, traits, score, probs, purity in rd["results"][:3]:
        print(f"    {bg:40} {traits} score={score:.3f} noise={purity:.2f} Dagger={probs['Dagger']:.3f}")

    print()
    print("=== Self-test 4: reverse derive multi [Heavy Armor, Shield, Trained] ===")
    rd2 = eng.reverse_derive(["Heavy Armor", "Shield", "Trained"], mode="analytic", top_n=5, tiebreak_limit=20, prune_threshold=20)
    print(f"  max_score={rd2['max_score']:.3f}, tied={rd2['tied_count']}, tiebreak={rd2.get('tiebreak_used')}")
    for bg, traits, score, probs, purity in rd2["results"][:3]:
        ha = probs['Heavy Armor']
        sh = probs['Shield']
        tr = probs['Trained']
        print(f"    {bg:40} {traits} score={score:.3f} HA={ha:.2f} Sh={sh:.2f} Tr={tr:.2f}")

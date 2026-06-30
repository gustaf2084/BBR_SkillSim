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

import random
from collections import OrderedDict, defaultdict
from copy import deepcopy

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

class SkillEngine:
    """技能树出现概率计算引擎。"""

    def __init__(self, game_data):
        """
        参数:
          game_data: GameData 实例（来自 data_loader.load_data）
        """
        self.gd = game_data
        self.big_weight = game_data.big_weight
        self.default_rolls = game_data.default_group_rolls
        # 预计算各类别组列表
        self._groups_by_cat = {}
        for cat in CATEGORY_ORDER:
            self._groups_by_cat[cat] = game_data.groups_by_category(cat)
        self._all_groups = list(game_data.groups.keys())

    # ------------------------------------------------------------------
    # 权重合成
    # ------------------------------------------------------------------

    def exclusive_cascade_weights(self, exclusive_group_name):
        """返回某专属组的级联权重修正 {group: weight}。"""
        ec = self.gd.exclusive_groups.get(exclusive_group_name, {})
        return dict(ec.get("other_weights", {}))

    def attribute_star_weight(self, group, talent_stars=None):
        """
        天赋星对组权重的修正。
        talent_stars: {attribute: stars} 或 None（用默认中值）。
        """
        if talent_stars is None:
            talent_stars = {a: DEFAULT_TALENT_STARS for a in self.gd.attribute_weights}
        w = 0.0
        for attr, stars in talent_stars.items():
            attr_map = self.gd.attribute_weights.get(attr, {})
            if group in attr_map:
                multiplier = attr_map[group]
                if multiplier > 0:
                    w += multiplier * stars
        return w

    def projected_attr_weight(self, group, projected=None):
        """
        投影属性对组权重的修正。
        projected: {attribute: value} 或 None（用默认中值）。
        规则: 若投影值超过 cutoff，权重 += base * (value - cutoff) 的某种近似。
        简化为: base * max(0, (value - cutoff) / 10) 作为加成（保守估计）。
        """
        proj = self.gd.projected_attributes.get(group)
        if not proj:
            return 0.0
        if projected is None:
            projected = DEFAULT_PROJECTED
        base = proj.get("base", 0.0)
        cutoff = proj.get("cutoff")
        if cutoff is None:
            # 无 cutoff 的组（如 Dagger/Shield 投影），用 base 作为基础权重
            return base
        # 找该组 governed by 的属性（按组名推断）
        gov_attr = self._group_governing_attr(group)
        val = projected.get(gov_attr, 0.0)
        if val > cutoff:
            # 每超过 cutoff 10 点加一个 base 的权重
            return base * max(0.0, (val - cutoff) / 10.0)
        return 0.0

    def _group_governing_attr(self, group):
        """根据组名推断投影属性受哪个属性管辖。"""
        # 武器组受 Melee Skill 管辖（远程武器受 Ranged Skill）
        if group in {"Bow", "Crossbow", "Throwing", "Ranged"}:
            return "Ranged Skill"
        if group == "Shield":
            return "Melee Defense"
        if group == "Fencer":
            return "Initiative"
        return "Melee Skill"

    def compute_raw_weight(self, bg_id, trait_ids, group,
                           exclusive_active=None, use_attribute=True, use_projected=True):
        """
        计算单个组的合成权重（未归一化）。
        exclusive_active: 当前已骰出的专属组名列表（用于级联）；None 表示不考虑级联。
        use_attribute / use_projected: 是否计入天赋星/投影属性修正。
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
            w += self.attribute_star_weight(group)

        # 投影属性
        if use_projected:
            w += self.projected_attr_weight(group)

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

    def num_rolls(self, bg_id, category):
        """某类别骰组数 = 默认基线 + 背景修正，最小 0。"""
        base = self.default_rolls.get(category, 0)
        bg = self.gd.backgrounds.get(bg_id, {})
        mod = bg.get("group_rolls", {}).get(category, 0)
        n = base + mod
        if isinstance(n, float):
            n = n  # Exclusive 基线 0.5 保留浮点
        return max(0.0, n)

    # ------------------------------------------------------------------
    # 专属组确定
    # ------------------------------------------------------------------

    def resolve_exclusive(self, bg_id, rng=None):
        """
        根据背景的 exclusive 配置，返回可能的专属组结果列表（带概率）。
        返回: [(exclusive_groups_list, probability), ...]
          - fixed: [([group], 1.0)]
          - prob:  [([g1], p1), ([g2], p2), ([], none_chance)]
          - mixed: forced 组必出 + prob 分支
          - none:  [([], 1.0)]
        """
        bg = self.gd.backgrounds.get(bg_id, {})
        exc = bg.get("exclusive", {"mode": "none"})
        mode = exc.get("mode", "none")

        if mode == "none":
            return [([], 1.0)]
        if mode == "fixed":
            return [([exc.get("group")], 1.0)]
        if mode == "prob":
            picks = exc.get("picks", {})
            none_chance = exc.get("none_chance", 0.0)
            total = sum(picks.values()) + none_chance
            if total <= 0:
                return [([], 1.0)]
            results = []
            for g, p in picks.items():
                results.append(([g], p / total))
            if none_chance > 0:
                results.append(([], none_chance / total))
            return results
        if mode == "mixed":
            forced = exc.get("forced", [])
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

    # ------------------------------------------------------------------
    # 出现概率（解析近似）
    # ------------------------------------------------------------------

    def _appear_prob_no_replacement(self, weights_dict, target, n):
        """
        无放回抽样的解析近似：类别内骰 n 组，计算 target 至少被抽中一次的概率。
        weights_dict: {group: weight}（仅正权重组）
        算法：逐轮计算"本轮未抽中 target"的概率并连乘。
          每轮，target 未被抽中的边际概率 = 1 - w_target/total。
          抽中非 target 组后，该组被移出，剩余权重重新归一。
          由于"抽中哪个非target组"会影响 target 后续权重占比，这里用按权重加权
          的期望更新（对 target 占比做一阶近似），在组数≤12、n≤5 时精度足够。
        """
        if target not in weights_dict or weights_dict[target] <= 0:
            return 0.0
        n_eff = int(round(n))
        if n_eff <= 0:
            return 0.0
        if len(weights_dict) == 1:
            return 1.0 if target in weights_dict else 0.0

        # 用状态：当前各组剩余权重。逐轮抽样，计算 target 至少被抽中一次。
        # 为保持解析性且避免组合爆炸，采用"权重加权期望"近似：
        #   每轮按当前权重抽一个组；若抽中 target，命中；否则移出该组，继续。
        #   对"未抽中 target"的路径，按各非target组被抽中的概率加权后续状态。
        # 用递归 + 记忆化（状态为 frozenset 剩余组）。
        from functools import lru_cache

        items = sorted(weights_dict.items(), key=lambda x: x[0])
        names = [it[0] for it in items]
        wts = [it[1] for it in items]
        target_idx = names.index(target) if target in names else -1
        if target_idx < 0:
            return 0.0

        # 记忆化：状态 = 剩余组的位掩码 + 已抽次数。返回 P(target 至少被抽中一次)
        @lru_cache(maxsize=None)
        def p_hit(mask, k):
            if k <= 0:
                return 0.0
            # 当前剩余组的权重
            idxs = [i for i in range(len(names)) if (mask >> i) & 1]
            if not idxs:
                return 0.0
            total = sum(wts[i] for i in idxs)
            if total <= 0:
                return 0.0
            # 本轮抽中 target 的概率
            p_target = wts[target_idx] / total if (mask >> target_idx) & 1 else 0.0
            # 本轮抽中非 target 组 i 的概率 → 后续状态
            p_miss_then_hit = 0.0
            for i in idxs:
                if i == target_idx:
                    continue
                pi = wts[i] / total
                new_mask = mask & ~(1 << i)
                p_miss_then_hit += pi * p_hit(new_mask, k - 1)
            # 若本轮抽中 target，命中；若抽中非target，后续命中
            return p_target + p_miss_then_hit

        full_mask = (1 << len(names)) - 1
        return p_hit(full_mask, n_eff)

    def appear_prob_analytic(self, bg_id, trait_ids, group,
                             use_attribute=True, use_projected=True):
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
        bg = gd.backgrounds.get(bg_id)
        if bg is None:
            return 0.0
        gdef = gd.groups.get(group)
        if gdef is None:
            return 0.0
        cat = gdef.get("category")
        if cat == "Always":  # General 恒出现
            return 1.0

        n = self.num_rolls(bg_id, cat)
        if n <= 0:
            return 0.0

        # 专属分支
        branches = self.resolve_exclusive(bg_id)
        total_prob = 0.0
        for exc_groups, branch_p in branches:
            if branch_p <= 0:
                continue
            # 合成该类别内所有组的权重
            cat_groups = self._groups_by_cat.get(cat, [])
            weights = {}
            for g in cat_groups:
                w = self.compute_raw_weight(
                    bg_id, trait_ids, g,
                    exclusive_active=exc_groups,
                    use_attribute=use_attribute, use_projected=use_projected,
                )
                if w > 0:
                    weights[g] = w
            if not weights:
                p_appear = 0.0
            else:
                p_appear = self._appear_prob_no_replacement(weights, group, n)
            total_prob += branch_p * p_appear
        return min(1.0, max(0.0, total_prob))

    # ------------------------------------------------------------------
    # 出现概率（蒙特卡洛）
    # ------------------------------------------------------------------

    def appear_prob_monte_carlo(self, bg_id, trait_ids, group,
                                samples=20000, seed=42,
                                use_attribute=True, use_projected=True):
        """蒙特卡洛模拟单组出现概率。"""
        rng = random.Random(seed)
        gd = self.gd
        bg = gd.backgrounds.get(bg_id)
        if bg is None:
            return 0.0
        gdef = gd.groups.get(group)
        if gdef is None:
            return 0.0
        cat = gdef.get("category")
        if cat == "Always":
            return 1.0
        n = self.num_rolls(bg_id, cat)
        if n <= 0:
            return 0.0
        n_int = int(round(n))

        branches = self.resolve_exclusive(bg_id)
        # 归一化分支概率
        bp_sum = sum(p for _, p in branches)
        if bp_sum <= 0:
            branches = [([], 1.0)]
            bp_sum = 1.0

        hit = 0
        cat_groups = self._groups_by_cat.get(cat, [])
        for _ in range(samples):
            # 选专属分支
            r = rng.random() * bp_sum
            acc = 0.0
            chosen_exc = []
            for exc_groups, p in branches:
                acc += p
                if r <= acc:
                    chosen_exc = exc_groups
                    break
            # 合成权重
            weights = []
            names = []
            for g in cat_groups:
                w = self.compute_raw_weight(
                    bg_id, trait_ids, g,
                    exclusive_active=chosen_exc,
                    use_attribute=use_attribute, use_projected=use_projected,
                )
                if w > 0:
                    weights.append(w)
                    names.append(g)
            if not weights:
                continue
            total_w = sum(weights)
            # 无放回抽样 n_int 次
            chosen = set()
            w_copy = list(weights)
            n_copy = list(names)
            for _k in range(min(n_int, len(n_copy))):
                if not n_copy:
                    break
                tw = sum(w_copy)
                if tw <= 0:
                    break
                rr = rng.random() * tw
                a = 0.0
                idx = 0
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

    def forward_simulate(self, bg_id, trait_ids,
                         mode="analytic", use_attribute=True, use_projected=True,
                         samples=20000, seed=42):
        """
        正向模拟：给定背景+特性，返回所有组的出现概率分布。
        返回:
          OrderedDict {group: prob}（按概率降序、组名升序），或
          None 表示无可用方案（所有可骰类别都无可用组）。
        """
        gd = self.gd
        if bg_id not in gd.backgrounds:
            return None
        if bg_id not in gd.complete_backgrounds():
            return None

        results = OrderedDict()
        any_available = False
        for group in self._all_groups:
            gdef = gd.groups.get(group, {})
            cat = gdef.get("category")
            if cat == "Always":
                results[group] = 1.0
                any_available = True
                continue
            if mode == "monte_carlo":
                p = self.appear_prob_monte_carlo(
                    bg_id, trait_ids, group, samples=samples, seed=seed,
                    use_attribute=use_attribute, use_projected=use_projected)
            else:
                p = self.appear_prob_analytic(
                    bg_id, trait_ids, group,
                    use_attribute=use_attribute, use_projected=use_projected)
            results[group] = p
            if p > 0:
                any_available = True

        if not any_available:
            return None

        # 排序：概率降序，组名升序
        sorted_items = sorted(results.items(), key=lambda x: (-x[1], x[0]))
        return OrderedDict(sorted_items)

    def forward_reason_if_none(self, bg_id, trait_ids):
        """若正向模拟无可用方案，返回原因说明字符串。"""
        gd = self.gd
        bg = gd.backgrounds.get(bg_id, {})
        reasons = []
        # 检查各特性是否禁用了大量组
        for tid in trait_ids:
            t = gd.traits.get(tid, {})
            zeros = [g for g, w in t.get("weights", {}).items() if w == 0.0]
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

    def reverse_derive(self, target_groups, weights=None,
                       mode="analytic", multi_trait=False, max_traits=2,
                       use_attribute=True, use_projected=True,
                       top_n=None, tiebreak_limit=20):
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
        返回:
          {
            "max_score": float,
            "tied_count": int,           # 并列最大组合总数（排序前）
            "results": [(bg_id, (trait_ids,), score, group_probs, purity), ...]
                       按 背景名升序、特性名升序、干扰分升序 排列
          }
          或 {"max_score": 0, "results": [], "tied_count": 0} 表示无任何组合可生成目标组。
        """
        gd = self.gd
        if weights is None:
            weights = {g: 1.0 for g in target_groups}
        bgs = gd.complete_backgrounds()
        trait_names = sorted(gd.traits.keys())

        # 构造待遍历的特性组合
        if not multi_trait:
            trait_combos = [[]] + [[t] for t in trait_names]
        else:
            from itertools import combinations
            trait_combos = [[]]
            for k in range(1, max_traits + 1):
                for combo in combinations(trait_names, k):
                    trait_combos.append(list(combo))

        best_score = 0.0
        best_results = []

        for bg_id in bgs:
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
                if score > best_score + EPS:
                    best_score = score
                    best_results = [(bg_id, tuple(combo), score, group_probs)]
                elif abs(score - best_score) <= EPS and best_score > 0:
                    best_results.append((bg_id, tuple(combo), score, group_probs))

        tied_count = len(best_results)
        if best_score <= 0 or not best_results:
            return {"max_score": 0.0, "results": [], "tied_count": 0}

        # 并列过多时，计算"次要组干扰分"(purity) 用于次级排序
        # purity = 该组合下非目标组的出现概率总和（越小越纯粹，越靠前）
        use_tiebreak = tied_count > tiebreak_limit
        scored = []
        for bg_id, combo, score, group_probs in best_results:
            purity = 0.0
            if use_tiebreak:
                # 计算非目标组的总出现概率
                for g in self._all_groups:
                    if g in target_groups:
                        continue
                    gdef = gd.groups.get(g, {})
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

        # 排序：背景名升序、特性名升序、干扰分升序（purity 小=更纯粹=更靠前）
        scored.sort(key=lambda x: (x[0], list(x[1]), x[4]))
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

    def score_combination(self, bg_id, trait_ids, target_groups, weights=None,
                          mode="analytic", use_attribute=True, use_projected=True):
        """计算某背景+特性组合对目标组集合的加权得分。"""
        if weights is None:
            weights = {g: 1.0 for g in target_groups}
        score = 0.0
        probs = {}
        for g in target_groups:
            if mode == "monte_carlo":
                p = self.appear_prob_monte_carlo(bg_id, trait_ids, g,
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
    from data_loader import load_data
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    gd = load_data(os.path.join(here, "data.json"))
    eng = SkillEngine(gd)

    print("=== 自测1: adventurous_noble + [] 正向模拟（analytic 无放回）===")
    res = eng.forward_simulate("adventurous_noble_background", [], mode="analytic")
    if res:
        for g, p in list(res.items())[:12]:
            print(f"  {g:20} {p:.3f}")
        print(f"  ... 共 {len(res)} 组")
    else:
        print("  无可用方案")

    print("\n=== 自测2: analytic vs monte_carlo 一致性 (assassin, []) ===")
    for g in ["Dagger", "Light Armor", "Cleaver", "Hammer", "Mace", "Axe", "Sword"]:
        pa = eng.appear_prob_analytic("assassin_background", [], g)
        pm = eng.appear_prob_monte_carlo("assassin_background", [], g, samples=30000, seed=42)
        print(f"  {g:14} analytic={pa:.3f}  monte={pm:.3f}  diff={abs(pa-pm):.3f}")

    print("\n=== 自测3: 反向推导 Dagger（加次序）===")
    rd = eng.reverse_derive(["Dagger"], mode="analytic", top_n=10, tiebreak_limit=20)
    print(f"  max_score={rd['max_score']:.3f}, 并列总数={rd['tied_count']}, 启用加次序={rd.get('tiebreak_used')}")
    for bg, traits, score, probs, purity in rd["results"][:10]:
        print(f"    {bg:40} {traits} score={score:.3f} 干扰={purity:.2f} Dagger={probs['Dagger']:.3f}")

    print("\n=== 自测4: 反向推导多目标 [Heavy Armor, Shield, Trained] ===")
    rd2 = eng.reverse_derive(["Heavy Armor", "Shield", "Trained"], mode="analytic", top_n=5, tiebreak_limit=20)
    print(f"  max_score={rd2['max_score']:.3f}, 并列总数={rd2['tied_count']}, 启用加次序={rd2.get('tiebreak_used')}")
    for bg, traits, score, probs, purity in rd2["results"][:5]:
        ha = probs['Heavy Armor']; sh = probs['Shield']; tr = probs['Trained']
        print(f"    {bg:40} {traits} score={score:.3f} HA={ha:.2f} Sh={sh:.2f} Tr={tr:.2f}")

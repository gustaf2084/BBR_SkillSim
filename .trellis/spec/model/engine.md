# SkillEngine 概率引擎规范

适用时机:修改 `src/engine.py`(概率核心)或其调用方。

## 权重合成(Weight Synthesis)

`compute_raw_weight()`(`engine.py:316`)是单一合成路径:每组基础概率 × 自身权重,再叠加背景倍率、特性权重、天赋星权重、投影属性权重、专属组级联。特性权重语义:`"+"` = 强提升(`big_weight`,默认 10.0,来自 `GameData.big_weight`);`"0"` = 禁用该组。

- 任何权重来源为零 ⇒ 该组被移除
- `melee_only` 背景清零所有远程组
- 反模式:在 `compute_raw_weight()` 之外另写一套"简化的"权重计算 —— 两个计算模式共享这条路径,绕过它会导致 analytic 与 Monte Carlo 结果分叉

## 双计算模式及其一致性(必须保持)

- **analytic**:`appear_prob_analytic()`(`engine.py:550`)+ `_appear_prob_no_replacement()`(`engine.py:467`)。刻意实现为无放回抽样的递归 + 记忆化,不是近似公式 `1-(1-p)^n`
- **Monte Carlo**:`appear_prob_monte_carlo()`(`engine.py:701`)+ `_forward_monte_carlo_all()`(`engine.py:760`)。整角色联合模拟,20000 样本、固定随机种子
- 两种模式结果必须匹配,这是产品承诺(`tests/test_engine.py` 有对照用例)。新增权重来源时两种模式都要验证

## 分数 roll 数语义

`num_rolls()`(`engine.py:381`)支持分数(如 Exclusive 类别基线 0.5):分数 f 表示"有 f 概率多一次 roll",即 `P = (1-f)·P(⌊n⌋) + f·P(⌊n⌋+1)`。不要在调用侧自行 round/floor 掉小数。

## 专属组保证与覆盖

`resolve_exclusive()`(`engine.py:394`)与 `_get_guaranteed_exclusive_probs()`(`engine.py:441`):固定/概率/混合的"保证专属组"**覆盖**普通 Exclusive 类别的 roll 概率,两者不叠加。修改 Exclusive 逻辑时不得让保证组与常规 roll 叠加。

## 逆向推导(Reverse Derive)

`reverse_derive()`(`engine.py:1005`):两阶段剪枝 —— 先无特性评分全部背景、保留 top N,再只对入选背景展开特性组合;按背景去重;纯度(非目标组噪音)是次要排序,在 `reverse_derive()` 内部计算(`engine.py:1138-1152`)时复用 `forward_simulate()` 命中 forward 缓存(analytic 走 LRU、MC 联合模拟一次出全组)。注意 `score_combination()`(`engine.py:1169`)是逐目标组调 `appear_prob_analytic`/`appear_prob_monte_carlo` 的直接评分,不走 forward 缓存 —— 改评分逻辑时想命中缓存应复用 forward 路径,不要绕过。

## 缓存与线程安全契约(关键)

`SkillEngine.__init__`(`engine.py:101`)持有六个实例级缓存:

| 缓存 | 结构 | 容量 |
|---|---|---|
| `_forward_cache` | OrderedDict(LRU) | 200 |
| `_norepl_cache` | dict(FIFO) | 50000 |
| `_pool_cache` | dict(FIFO) | 20000 |
| `_base_weight_cache` | OrderedDict(LRU) | 20000 |
| `_bg_stars_cache` | dict | — |
| `_bg_proj_cache` | dict | — |

**`SkillEngine` 不是线程安全的。** 规则:

- 工作线程必须自行构造引擎实例,共享只读的 `GameData` —— 例:`tab_reverse.py:54` `self.engine = SkillEngine(engine.gd)`
- 引擎方法返回的 dict/列表是缓存共享对象,调用方**禁止修改**
- 反模式:在主线程建一个引擎、把结果丢进 QThread 里"顺手算一下";或在 UI 线程长调用 `reverse_derive()`(应走 QThread worker + 取消回调,见 `tab_reverse.py` 的 `ReverseDeriveWorker`)
- 新增缓存遵循既有命名(`_xxx_cache`)与淘汰策略(容量上限 + LRU/FIFO),并同步更新本表

## 参考

- 行为契约:根 `CLAUDE.md` Model layer 节;权威 changelog:`src/docs/开发文档.md`
- 测试:`tests/test_engine.py`(含 analytic/MC 对照、分数 roll、fractional 用例)

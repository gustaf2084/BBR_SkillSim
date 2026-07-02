# BBR_SkillSim v0.1.0 — 战场兄弟重铸技能树概率模拟器

Battle Brothers Reforged 模组的角色 build 概率分析工具。输入背景和特性，正向推演各技能树组出现概率，或反向推导达到指定技能树组的最佳组合。

## 功能

- **正向模拟** — 选背景 + 特性，计算所有技能树组的出现概率分布，展示技能树预览
- **反向推导** — 选目标技能树组（可多选），找出最佳背景+特性组合
- **流派推荐** — 浏览各背景的高概率技能树组参考，支持自定义流派方案文件
- **技能树可视化** — 7 阶矩阵展示每个组的 perk 树，带图标和中/英文描述
- **导出功能** — 复制结果文本或导出 CSV 文件

## 快速开始

### Windows 用户（推荐）

下载 Release 中的 `BBR_SkillSimulator-vX.X.X.exe`，放到任意目录运行即可。

**首次运行提示：**
1. exe 启动时会解压临时文件，可能需要 5-10 秒
2. 同级目录下需要 `data.json`、`perk_trees.json`、`perk_i18n.json` 和 `icons/` 文件夹（Release 包已包含）
3. **用户自定义数据：** 将自定义的 `data.json` 放在 exe 同级目录会优先加载

### 开发者运行

```bash
pip install -r requirements.txt
cd src
python main.py
```

### 打包

```bash
pip install -r requirements-dev.txt
cd src
pyinstaller build_safe.spec
```

## 使用指南

### 正向模拟（Forward）

1. 选择目标背景（可用搜索框快速定位）
2. 勾选特性（最多 3 个），特性网格支持搜索筛选
3. 点击「计算概率分布」
4. 结果表格展示各技能树组的出现概率，点击行可在下方查看该组完整技能树
5. 可通过「复制文本」或「导出 CSV」保存结果

**概率图例：**
- 绿色 ≥80%：几乎必然出现
- 棕色 50-80%：多数情况出现
- 蓝灰 20-50%：有希望但不稳定
- 灰色 <20%：不推荐依赖
- 浅灰 0%：无法生成

### 反向推导（Reverse）

1. 展开目标类别面板，勾选想要的技能树组（可多选）
2. 面板内支持搜索筛选
3. 可选：启用「允许多特性组合」以搜索 2-特质组合（速度较慢）
4. 点击「推导最佳组合」
5. 结果按概率得分降序排列，「次要组干扰」越低表示越纯粹

**解读结果：**
- **高得分 + 低干扰**：最佳选择，目标组概率高且干扰少
- **高得分 + 高干扰**：目标组概率高但附带大量非目标组（可能需要权衡）
- **双击结果行**：弹窗显示该组合的完整正向模拟结果

### 流派推荐（Builds）

1. 选择背景，自动展示高概率技能树组分析
2. 点击「+ 新建流派」创建自定义流派文件
3. 流派文件存放在 `builds/` 目录，可直接编辑文本文件

## 常见问题

**Q: 为什么某些背景不显示？**
A: 数据不完整的背景（缺少必要字段）已被隐藏，可在「关于」页查看隐藏列表。

**Q: 蒙特卡洛模式和解析近似有什么区别？**
A: 解析近似速度快（毫秒级），精度在日常使用中足够（与蒙特卡洛误差 <0.005）。蒙特卡洛模式运行 20000 次采样，更精确但较慢（秒级）。

**Q: 反向推导的「次要组干扰」是什么意思？**
A: 干扰值衡量非目标组的累积概率与目标组概率之比。值越低越纯粹。0-0.5 表示目标组是唯一高概率组；>2.0 表示多个非目标组也有高概率，目标不专一。

**Q: 可以在 Linux/Mac 上运行吗？**
A: 源代码是跨平台的（Python + PySide6），可直接 `python main.py` 运行。但 Release EXE 仅支持 Windows。

**Q: 如何更新游戏数据？**
A: 替换 `data.json`、`perk_trees.json`、`perk_i18n.json` 和 `icons/` 文件夹即可。数据格式需与当前版本兼容（参见下方数据结构说明）。

**Q: 结果显示「无可用方案」是什么情况？**
A: 该背景+特性组合因约束条件（如 melee_only 限制远程组权重为 0）导致无有效技能树组生成。尝试更换背景或减少特性。

## 项目结构

```text
BBR_SkillSim/
├── VERSION              # 版本号
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml       # ruff + mypy + pytest 配置
├── .github/workflows/   # GitHub Actions CI
├── tests/               # 单元测试 (pytest)
│   ├── test_engine.py
│   └── test_data_loader.py
└── src/
    ├── main.py          # 入口
    ├── main_window.py   # 主窗口（导航、快捷键、窗口状态持久化）
    ├── engine.py        # 概率引擎（解析近似 + 蒙特卡洛模拟 + 反向推导剪枝）
    ├── data_loader.py   # 数据加载与验证（含懒加载 perk_trees）
    ├── i18n.py          # 中/英文翻译
    ├── data.json        # 结构化数据（背景/特性/技能树组）
    ├── perk_trees.json  # 技能树数据（分离加载，减小内存占用）
    ├── perk_i18n.json   # 技能中文翻译（JSON 数据层）
    ├── icon_provider.py # 图标加载
    ├── skill_tree_widget.py  # 技能树矩阵可视化
    ├── perk_zh.py       # 技能翻译兼容层
    ├── tab_forward.py   # 正向模拟页
    ├── tab_reverse.py   # 反向推导页
    ├── tab_builds.py    # 流派推荐页
    ├── tab_about.py     # 关于页
    ├── build_safe.spec  # PyInstaller 打包配置
    └── build_simple.bat # 一键打包脚本
```

## 开发者文档

### 概率引擎算法

**正向模拟（解析近似）：**
1. 根据背景和特性计算各组权重：raw_weight = (base_p * multiplier) * attribute_weight * projected_attribute + trait_weights
2. 处理专属组：对每个 exclusive 分支，按级联权重分配
3. 类别内无放回抽样：从该类别骰 n 组（n = group_rolls + exclusive_half_roll），计算每个组至少被抽中一次的概率
4. 无放回近似采用一阶矩近似：每轮按权重比例加权更新剩余组的期望权重占比

**反向推导（两阶段剪枝）：**
1. Phase 1：对所有背景（无特性）计算目标组综合得分，按得分排序取 top N
2. Phase 2：仅对 top N 候选背景展开特性组合（single 或 multi-trait），计算完整得分
3. 按次要组干扰（side-group noise = 非目标组总概率 / 目标组总概率）排序，干扰越小越纯粹

**LRU 缓存策略：**
- 正向模拟结果缓存（容量 200），基于 (bg_id, trait_ids tuple, mode parameters) 复合键
- 无放回采样子结果缓存，基于 (target, weight_signature, n_eff, mask, k) 复合键

### data.json 结构

顶层键：`meta`, `config`, `backgrounds`, `traits`, `groups`, `exclusive_groups`, `attribute_weights`, `projected_attributes`, `perk_trees`（可分离到 perk_trees.json）, `builds`

**groups 分类体系（category 字段）：**
- `Shared` — 共有组（如 General）
- `Exclusive` — 专属组（如 Noble, Knave）
- `Weapon` — 武器组（如 Axe, Dagger）
- `Armor` — 护甲组（如 Heavy Armor, Light Armor）
- `Fighting Style` — 战斗风格（如 Trained, Tactician）
- `Special` — 特殊组（如 Alchemist）
- `Always` — 常驻组（概率恒为 1）

**background 关键字段：**
- `group_rolls` — 每类别的出组数量配置
- `multipliers` — 组权重系数
- `base_probabilities` — 基础概率
- `melee_only` — 是否只生成近战组
- `exclusive` — 所属专属组列表

**trait 关键字段：**
- `weights` — 对各组的权重加成

### 运行测试

```bash
cd BBR_SkillSim
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

### 版本号规则

- VERSION 文件为单一数据源
- `python main.py` 读取 VERSION 文件显示版本
- CI 构建时从 git tag 自动注入版本号（v0.1.0 → VERSION=0.1.0）
- 手动构建时从 VERSION 文件读取

## 数据来源

基于 Battle Brothers Reforged 0.7.6 模组数据解析生成，技能图标来自原版 BB Wiki 和 Reforged 模组资源。

## License

仅供个人学习和模组研究使用。

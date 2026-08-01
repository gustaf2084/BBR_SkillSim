# 代码复用思考指南(BBR_SkillSim)

> **目的**:写新代码前先想 —— 项目里是否已有现成实现?

---

## 本项目的高价值复用点

### 1. 引擎计算路径(禁止另起炉灶)

`compute_raw_weight()`(`engine.py:316`)是唯一权重合成路径,analytic 与 Monte Carlo **共享**它。任何"简化的权重计算"都会导致双模式结果分叉。

`forward_simulate()`(`engine.py:811`)是权威的前向模拟入口,带缓存:

- 逆向推导的纯度评分直接复用 `forward_simulate()` 命中 forward 缓存(`reverse_derive()` 内部纯度计算,`engine.py:1138-1152`;`score_combination()` 是逐组直算路径,不走缓存)
- **反模式**:逆向路径里手写一遍"简化版前向计算" —— 性能掉一个量级且结果可能与引擎不一致

### 2. 数据访问器(禁止直接摸 dict)

`GameData` 提供的访问器是全项目唯一入口:

- 显示名:`bg_name()` / `trait_name()` / `group_name()`(`data_loader.py:220/225/230`,双语)
- 完整/过滤列表:`complete_backgrounds()`(`:238`)、`filtered_complete_backgrounds()`(`:242`)
- 反模式:UI 里直接 `gd.backgrounds[bg_id]["name"]` 拼显示名 —— 语言切换不更新、绕过隐藏逻辑

### 3. 通用 UI 组件(ui_components.py)

写占位/提示/折叠 UI 前先查 `src/ui_components.py`:`make_placeholder`(`:12`)、`make_notice_parchment`(`:49`)、`make_error_notice`(`:70`)、`CollapsibleSection`(`:90`)。已有 80% 相似组件时扩展它,不新建。

### 4. 常量单一来源

| 常量 | 唯一来源 |
|---|---|
| 颜色 | `theme.py` LIGHT/DARK token(禁止字面量) |
| 用户可见字符串 | `i18n.py` `_add()` 词条(禁止硬编码) |
| 版本号 | 根 `VERSION` 文件 |
| 设置文件名 | `data_loader.py` `SETTINGS_FILE` |
| 应用路径 | `app_paths.py`(禁止重复实现 `_MEIPASS` 探测) |

### 5. 双语名称包装

perk 名/描述通过 `perk_zh.py` 包装层读 `perk_i18n.json`,UI 不直接操作该 json。

---

## 何时抽象、何时不抽象

**抽象**(项目实例):

- 权重合成、概率计算 —— 逻辑复杂、两种模式必须一致 ⇒ 单一路径 + 缓存
- 路径解析、设置持久化 —— 多场景复用且打包后行为不同 ⇒ `app_paths.py` / `data_loader` 的 settings 函数

**不要抽象**:

- 只在单 tab 用一次的简单展示逻辑(留在该 tab)
- 把 `i18n.t()` 再包一层"专用取词函数" —— 直接用 `t()` 即可

---

## 复用检查清单(提交前)

- [ ] 搜索过既有实现:`rg "函数名|关键字" src/ tests/`
- [ ] 没有复制粘贴本应共享的逻辑(权重合成、概率计算、双语访问、路径解析)
- [ ] 常量定义在一处(颜色/词条/版本/设置名/路径)
- [ ] 相似控件遵循同一结构(参照 `ui_components.py` 与各 tab 的 `on_data_ready` 签名)

---

## 反模式速查

- 另写一套权重/概率计算(双模式分叉)
- 直接读 `gd._data` 或背景 dict 原始字段拼显示名
- 手写 `_MEIPASS`/`sys.executable` 路径逻辑
- UI 文案硬编码中文/英文
- 逆向推导里重新实现前向模拟

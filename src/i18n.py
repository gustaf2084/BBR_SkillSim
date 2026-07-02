# -*- coding: utf-8 -*-
"""i18n.py — centralized Chinese/English translation strings.

Usage:
    from i18n import t, set_lang, lang
    label = QLabel(t("forward.char_config"))
    set_lang("en")  # switch to English
"""

import theme

# ── Translation dictionary ──────────────────────────────────────

_TR = {}

def _add(key, zh, en):
    _TR[key] = {"zh": zh, "en": en}

# ── shared: category names ──
_add("cat.shared",         "共有组",               "Shared")
_add("cat.exclusive",      "专属组",               "Exclusive")
_add("cat.weapon",         "武器组",               "Weapon")
_add("cat.armor",          "护甲组",               "Armor")
_add("cat.fighting_style", "战斗风格",              "Fighting Style")
_add("cat.special",        "特殊组",               "Special")
_add("cat.always",         "常驻",                 "Always")
_add("cat.shared_short",   "共有",                 "Shared")
_add("cat.exclusive_short","专属",                 "Exclusive")
_add("cat.weapon_short",   "武器",                 "Weapon")
_add("cat.armor_short",    "护甲",                 "Armor")
_add("cat.style_short",    "风格",                 "Style")
_add("cat.special_short",  "特殊",                 "Special")

# ── shared: probability tier labels ──
_add("prob.high",    "大概率",  "Very Likely")
_add("prob.likely",  "较可能",  "Likely")
_add("prob.chance",  "看运气",  "Uncertain")
_add("prob.low",     "小概率",  "Unlikely")
_add("prob.none",    "不出现",  "None")

# ── shared: mode ──
_add("mode.analytic", "快速（解析近似）",       "Fast (analytic approx.)")
_add("mode.monte",    "精确（蒙特卡洛）",        "Exact (Monte Carlo)")
_add("mode.monte_slow","精确（蒙特卡洛，较慢）",  "Exact (Monte Carlo, slower)")

# ── shared: common ──
_add("common.none_solution", "无可用方案",        "No valid build")
_add("common.no_traits",     "（无）",             "(none)")
_add("common.ok",            "确定",               "OK")
_add("common.notice",        "提示",               "Notice")
_add("common.error",         "错误",               "Error")
_add("common.mode_label",    "计算模式:",           "Mode:")
_add("common.copied",        "已复制到剪贴板",       "Copied to clipboard")
_add("common.cancel",        "取消",               "Cancel")
_add("common.calculating",   "计算中…",             "Calculating...")

# ── nav / window chrome ──
_add("nav.title",       "技能模拟器",   "Skill Simulator")
_add("nav.forward",     "正向模拟",     "Forward Sim")
_add("nav.reverse",     "反向推导",     "Reverse Derive")
_add("nav.builds",      "流派推荐",     "Builds")
_add("nav.about",       "关于",         "About")
_add("theme.to_dark",   "深色模式",     "Dark Mode")
_add("theme.to_light",  "浅色模式",     "Light Mode")
_add("theme.tip_dark",  "切换到深色主题", "Switch to dark theme")
_add("theme.tip_light", "切换到浅色主题", "Switch to light theme")
_add("status.data_version", "数据版本 ", "Data version ")

# ── forward tab ──
_add("forward.char_config",   "角色配置",            "Character Setup")
_add("forward.traits_count",  "特性 (已选 {0}/3):",   "Traits (selected {0}/3):")
_add("forward.guide_title",   "开始你的第一次模拟",    "Start your first simulation")
_add("forward.guide_body",
      "① 在左侧选择背景　→　② 勾选特性(可选,最多 3 个)　→　③ 点击「计算概率分布」",
      "1. Pick a background on the left   2. Check traits (optional, max 3)   "
      "3. Click \"Calculate Distribution\"")
_add("forward.bg_search_ph",  "输入搜索背景...",      "Type to search backgrounds...")
_add("forward.bg_label",      "背景:",               "Background:")
_add("forward.traits_label",  "特性 (最多3个):",       "Traits (max 3):")
_add("forward.advanced",      "高级选项",             "Advanced")
_add("forward.use_attr",      "计入天赋星修正",        "Apply talent star modifiers")
_add("forward.use_proj",      "计入投影属性修正",      "Apply projected attribute modifiers")
_add("forward.calc_btn",      "计算概率分布",          "Calculate Distribution")
_add("forward.result_title_ph","请在左侧选择背景与特性，点击「计算概率分布」",
      "Select a background and traits on the left, then click Calculate")
_add("forward.none_title",    "无可用方案",            "No valid build")
_add("forward.table_caption", "概率分布表（点击行查看下方技能树）",
      "Probability distribution (click a row to view the skill tree below)")
_add("forward.result_none",   "正向模拟结果：无可用方案", "Forward simulation: no valid build")
_add("forward.result_ok_prefix","正向模拟结果：",       "Forward: ")
_add("forward.trait_limit_title","提示",              "Notice")
_add("forward.trait_limit_body", "特性最多选择 3 个。", "You can select at most 3 traits.")
_add("forward.calc_err_title",   "计算错误",          "Calculation Error")
_add("forward.calc_err_prefix",  "计算过程出错：",      "An error occurred during calculation")
_add("forward.h_icon",       "图标",                  "Icon")
_add("forward.h_group",      "技能树组",              "Skill Tree Group")
_add("forward.h_category",   "类别",                  "Category")
_add("forward.h_probability","出现概率",              "Probability")
_add("forward.h_bar",        "概率条",                "Bar")
_add("forward.trait_search_ph","筛选特性...",         "Filter traits...")
_add("forward.copy_btn",     "复制文本",              "Copy Text")
_add("forward.export_btn",   "导出CSV",               "Export CSV")
_add("forward.export_title", "导出正向模拟结果",       "Export Forward Results")

# ── v0.3.0: Forward tab attribute range panel ──
_add("attr.hitpoints",    "生命值",  "Hitpoints")
_add("attr.fatigue",      "疲劳",   "Fatigue")
_add("attr.bravery",      "决心",   "Bravery")
_add("attr.initiative",   "主动值",   "Initiative")
_add("attr.melee_skill",  "近战技能", "Melee Skill")
_add("attr.ranged_skill", "远程技能", "Ranged Skill")
_add("attr.melee_defense","近战防御", "Melee Defense")
_add("attr.ranged_defense","远程防御","Ranged Defense")
_add("attr.range_title",  "属性范围", "Attribute Range")
_add("attr.estimated",    "估算值",  "Estimated")
_add("attr.missing",      "属性数据待补", "Attribute data unavailable")

# ── v0.3.0: Forward tab talent star adjustment ──
_add("forward.talent_stars",   "天赋星级调节", "Talent Stars")
_add("star.0", "0星", "0★")
_add("star.1", "1星", "1★")
_add("star.2", "2星", "2★")
_add("star.3", "3星", "3★")

# ── reverse tab ──
_add("reverse.target_title", "目标技能树组（可多选）", "Target Skill Tree Groups (multi-select)")
_add("reverse.advanced",     "高级选项",               "Advanced")
_add("reverse.multi_trait",  "允许多特性组合（最多2个，较慢）",
      "Allow multi-trait combos (max 2, slower)")
_add("reverse.topn_label",   "返回数量:",              "Result count:")
_add("reverse.derive_btn",   "推导最佳组合",            "Derive Best Combos")
_add("reverse.result_title_ph","选择目标技能树组，点击推导",
      "Select target groups, then click Derive")
_add("reverse.h_bg",         "背景",                   "Background")
_add("reverse.h_traits",     "特性",                   "Traits")
_add("reverse.h_score",      "概率/得分",              "Prob/Score")
_add("reverse.h_purity",     "次要组干扰",             "Side-group Noise")
_add("reverse.empty_title",  "无可用组合",              "No valid combination")
_add("reverse.empty_body",   "该目标组无任何背景+特性组合可生成。",
      "No background+trait combination can generate these target groups.")
_add("reverse.result_none",  "反向推导结果：无可用组合",  "Reverse derivation: no valid combination")
_add("reverse.result_ok_prefix","反向推导：",          "Reverse: ")
_add("reverse.need_target_title","提示",               "Notice")
_add("reverse.need_target_body", "请至少选择一个目标技能树组。",
      "Select at least one target group.")
_add("reverse.err_title",    "推导错误",               "Derivation Error")
_add("reverse.err_prefix",   "推导过程出错：",          "An error occurred during derivation")
_add("reverse.summary_max",  "最大概率/得分：",         "Max prob/score: ")
_add("reverse.summary_tied", "最高分并列：{0} 个",     "Peak-score ties: {0}")
_add("reverse.summary_returned","返回：{0} 个（已去重）", "Returned: {0} (deduped)")
_add("reverse.summary_topn", "按得分降序返回前 {0} 个",  "Top {0} by score (descending)")
_add("reverse.summary_noise","（已按次要组干扰排序，干扰越小越纯粹）",
      "(sorted by side-group noise; lower is purer)")
_add("reverse.purity_low_tip","非常纯粹，目标组是唯一高概率组",
      "Very pure - target group is the only high-probability group")
_add("reverse.purity_high_tip","干扰严重，多个非目标组也有较高概率",
      "Heavy noise - several non-target groups also have high probability")
_add("reverse.dlg_none_title","无可用方案",            "No Valid Build")
_add("reverse.dlg_none_body", "该组合无可用方案。",     "This combination has no valid build.")
_add("reverse.dlg_title_prefix","详细概率分布 — ",      "Detailed Probability Distribution - ")
_add("reverse.dlg_bg_label",  "背景：",                "Background: ")
_add("reverse.dlg_traits_label","特性：",              "Traits: ")
_add("reverse.dlg_h_group",   "技能树组",              "Skill Tree Group")
_add("reverse.dlg_h_category","类别",                  "Category")
_add("reverse.dlg_h_prob",    "出现概率",              "Probability")
_add("reverse.search_ph",     "搜索组...",             "Search groups...")
_add("reverse.hint_dblclick", "💡 双击结果行可查看该组合的完整概率分布",
      "💡 Double-click a row to view the full probability distribution")
_add("reverse.progress_bg",   "正在处理背景 {0}/{1}…",  "Processing background {0}/{1}...")
_add("reverse.guide_title",   "从目标倒推最佳选人",     "Work backwards from your target")
_add("reverse.guide_body",
      "① 展开左侧类别面板,勾选目标技能树组(可多选)　→　② 点击「推导最佳组合」",
      "1. Expand a category panel and check target groups   "
      "2. Click \"Derive Best Combos\"")
_add("reverse.copy_btn",      "复制文本",              "Copy Text")
_add("reverse.export_btn",    "导出CSV",               "Export CSV")
_add("reverse.export_title",  "导出反向推导结果",       "Export Reverse Results")

# ── builds tab ──
_add("builds.bg_label",       "选择背景:",              "Select background:")
_add("builds.bg_search_ph",   "筛选背景...",            "Filter backgrounds...")
_add("builds.custom_label",   "自定义流派：",           "Custom Builds:")
_add("builds.new_btn",        "+ 新建流派",             "+ New Build")
_add("builds.edit_btn",       "编辑",                   "Edit")
_add("builds.folder_tip",     "打开 builds 文件夹",      "Open builds folder")
_add("builds.auto_title",     "自动数据分析",           "Auto Analysis")
_add("builds.card_defense",   "防御核心",               "Defense Core")
_add("builds.card_offense",   "攻击方向",               "Offense Direction")
_add("builds.card_special",   "特殊潜力",               "Special Potential")
_add("builds.card_ph",        "选择背景后自动分析",      "Auto-analysis appears after selecting a background")
_add("builds.card_none",      "（无可用方案）",          "(no valid build)")
_add("builds.card_empty",     "（无相关组）",            "(no relevant groups)")
_add("builds.page_title_prefix","流派推荐 — ",          "Build Recommendations - ")
_add("builds.guide",          "💡 想在 <b>builds/</b> 目录中创建流派方案文件，自定义推荐加点。点击「+ 新建流派」即可开始。",
      "💡 Create build files in the <b>builds/</b> folder to customize perk picks. Click \"+ New Build\" to start.")
_add("builds.traits_hint_prefix","推荐特性：",          "Recommended traits: ")
_add("builds.perk_low_tip",   "⚠ 低概率：建议搭配特性提升 {group} 组出现概率",
      "⚠ Low probability: add traits to raise the {group} group's chance")
_add("builds.parse_err_prefix","解析问题：",            "Parse issues:")
_add("builds.file_created_title","文件已创建",          "File Created")
_add("builds.file_created_body","流派文件已创建：\n{path}\n请用文本编辑器打开编辑。",
      "Build file created:\n{path}\nOpen it in a text editor to edit.")
_add("builds.open_err_title", "错误",                   "Error")
_add("builds.open_err_body",  "无法打开文件：",         "Cannot open file: ")
_add("builds.open_folder_err_title","错误",             "Error")
_add("builds.open_folder_err_body", "无法打开文件夹：",  "Cannot open folder: ")
_add("builds.perk_h_num",     "#",                      "#")
_add("builds.perk_h_group",   "技能树组",              "Skill Tree Group")
_add("builds.perk_h_tier",    "层级",                  "Tier")
_add("builds.perk_h_perk",    "技能名",                "Perk")
_add("builds.perk_h_prob",    "出现概率",              "Probability")

# ── about tab ──
_add("about.title",   "战场兄弟·重铸 — 技能树模拟器",
      "Battle Brothers: Reforged - Skill Tree Simulator")
_add("about.card_data","数据信息",                     "Data Info")
_add("about.card_features","功能说明",                 "Features")
_add("about.card_legend","概率图例",                   "Probability Legend")
_add("about.data_version","游戏数据版本：",             "Game data version: ")
_add("about.data_bg_count","背景数量：",                "Backgrounds: ")
_add("about.data_bg_avail","可用 ",                     "available ")
_add("about.data_bg_incomplete","不完整 ",              "incomplete ")
_add("about.data_trait_count","特性数量：",             "Traits: ")
_add("about.data_group_count","技能树组：",             "Skill tree groups: ")
_add("about.data_level","默认等级：",                   "Default level: ")
_add("about.data_skill_pts","{0} 技能点",              "{0} skill pts")
_add("about.data_hidden","不完整背景（已隐藏）：",      "Incomplete backgrounds (hidden): ")
_add("about.data_warnings","数据告警 {0} 条（详见日志）","Data warnings: {0} (see logs)")
_add("about.features_text",
      "<p><b>正向模拟</b>——选择背景与特性，查看所有可能生成的技能树组"
      "及其出现概率分布。用于招人前预判。</p>"
      "<p><b>反向推导</b>——选择目标技能树组，找出使其出现概率最大的"
      "背景+特性组合。从需求倒推选人。</p>"
      "<p><b>流派推荐</b>——自动分析各背景的技能树倾向，"
      "支持自定义流派方案文件（builds/*.txt）编辑与分享。</p>",
      "<p><b>Forward Sim</b> — select a background and traits to view all possible skill tree groups "
      "and their probability distribution. Helps pre-screen recruits.</p>"
      "<p><b>Reverse Derive</b> — select target skill tree groups and find the best "
      "background+trait combos that maximize their probability. Work backwards from your needs.</p>"
      "<p><b>Builds</b> — auto-analyze each background's skill tree tendencies, "
      "with support for custom build files (builds/*.txt) for editing and sharing.</p>")
_add("about.legend_high",   "大概率 ≥80%",  "Very Likely ≥80%")
_add("about.legend_high_d", "几乎必然出现",  "almost certain to appear")
_add("about.legend_likely",   "较可能 50–80%", "Likely 50–80%")
_add("about.legend_likely_d", "多数情况出现",  "usually appears")
_add("about.legend_chance",   "看运气 20–50%", "Uncertain 20–50%")
_add("about.legend_chance_d", "有希望但不稳",  "possible but unreliable")
_add("about.legend_low",   "小概率 <20%", "Unlikely <20%")
_add("about.legend_low_d", "不推荐依赖",   "don't rely on it")
_add("about.legend_none",   "不出现 =0", "None =0")
_add("about.legend_none_d", "无法生成",  "cannot be generated")
_add("about.legend_halo",
      "技能树节点外圈的光环弧长 = 该组出现概率(整圈 = 100%)。",
      "The halo arc around each skill node = the group's probability (full circle = 100%).")
_add("about.legend_tip",
      "提示：高概率不一定好（你可能不想要该组），低概率不一定坏（出了是惊喜）。",
      "Tip: high probability isn't always good (you may not want that group), "
      "low isn't always bad (a pleasant surprise).")

# ── skill tree widget ──
_add("st.placeholder",    "请选择一个背景并点击计算概率分布",
      "Select a background and click Calculate Distribution")
_add("st.chip_label",     "技能组：",                  "Skill Groups: ")
_add("st.add_btn",        "+ 添加组",                   "+ Add Group")
_add("st.all_shown",      "（所有组已显示）",           "(All groups shown)")
_add("st.legend",         "光环弧长 = 出现概率",        "Halo arc = probability")
_add("st.tier1", "1阶", "Tier 1")
_add("st.tier2", "2阶", "Tier 2")
_add("st.tier3", "3阶", "Tier 3")
_add("st.tier4", "4阶", "Tier 4")
_add("st.tier5", "5阶", "Tier 5")
_add("st.tier6", "6阶", "Tier 6")
_add("st.tier7", "7阶", "Tier 7")

# ── build_parser ──
_add("parser.read_fail",    "读取文件失败: ",          "Failed to read file: ")
_add("parser.bad_order",    "第 {0} 行：序号 '{1}' 不是数字",
      "Line {0}: order '{1}' is not a number")
_add("parser.bad_format",   "第 {0} 行：格式应为 '序号 = 组名, 层级, 技能名'",
      "Line {0}: expected 'order = Group, Tier, Perk'")

# ── main.py global error ──
_add("error.global_title",  "发生错误",                "Error Occurred")
_add("error.global_body",   "程序遇到未处理的错误：\n\n{0}\n\n详细信息已记录。\n\n{1}",
      "The program encountered an unhandled error:\n\n{0}\n\nDetails have been recorded.\n\n{1}")

# ── Language state ──
_current = "zh"


def set_lang(lang):
    """Switch display language. 'zh' or 'en'."""
    global _current
    _current = lang


def t(key):
    """Return the translation for key in the current language."""
    return _TR.get(key, {}).get(_current, key)


def lang():
    """Return current language code."""
    return _current


# ── Convenience: per-category translation ──
def cat_name(cat_en):
    """Translate a category's English name to the display language."""
    key_map = {
        "Shared": "cat.shared", "Exclusive": "cat.exclusive",
        "Weapon": "cat.weapon", "Armor": "cat.armor",
        "Fighting Style": "cat.fighting_style", "Special": "cat.special",
        "Always": "cat.always",
    }
    return t(key_map.get(cat_en, cat_en))


# ── Convenience: probability tier label ──
def prob_tier_label(p):
    """Return (label, color) for a probability value. Color follows the active theme."""
    color = theme.prob_color(p)
    if p >= 0.80:
        return t("prob.high"), color
    if p >= 0.50:
        return t("prob.likely"), color
    if p >= 0.20:
        return t("prob.chance"), color
    if p > 0:
        return t("prob.low"), color
    return t("prob.none"), color


def prob_tier_metal(p):
    """Return (label, color, metal_tag) for probability - reverse tab style."""
    color = theme.prob_color(p)
    if p >= 0.80:
        return t("prob.high"), color, "gold"
    if p >= 0.50:
        return t("prob.likely"), color, "copper"
    if p >= 0.20:
        return t("prob.chance"), color, "iron"
    if p > 0:
        return t("prob.low"), color, "gray"
    return t("prob.none"), color, "dark"

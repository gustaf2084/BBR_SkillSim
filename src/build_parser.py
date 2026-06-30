# -*- coding: utf-8 -*-
"""
build_parser.py
解析 builds/*.txt 流派方案文件。

文件格式：
    [build]
    name = 流派名称
    background = background_id
    traits = trait1, trait2  (可选)
    tags = 坦克, 防御  (可选)

    [perks]
    1 = GroupName, Tier 3, PerkName
    2 = ...
    ...

    [playstyle]
    自由文本，直到文件末尾或下一个 [section]

规则：
- 空行和 # 开头的行为注释，忽略
- 节标题 [xxx] 大小写不敏感
- 键值对用第一个 = 分割，键去首尾空格
- perks 节：序号 = 组名, 层级, 技能名
- 编码：UTF-8
"""

import os
import re


class BuildData:
    """一个流派方案的数据对象。"""
    def __init__(self):
        self.filename = ""
        self.name = ""
        self.background = ""
        self.traits = []       # list of trait_id
        self.tags = []         # list of str
        self.perks = []        # list of (order, group, tier, perk_name)
        self.playstyle = ""
        self.parse_errors = []  # list of str

    def is_valid(self):
        return bool(self.name and self.background and self.perks)


def parse_build_file(filepath):
    """解析单个 .txt 文件，返回 BuildData 或 None。"""
    if not os.path.isfile(filepath):
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        bd = BuildData()
        bd.filename = os.path.basename(filepath)
        bd.parse_errors.append(f"读取文件失败: {e}")
        return bd

    bd = BuildData()
    bd.filename = os.path.basename(filepath)
    current_section = None

    for lineno, raw in enumerate(lines, 1):
        line = raw.strip()

        # 空行和注释
        if not line or line.startswith("#"):
            continue

        # 节标题
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip().lower()
            continue

        # 无章节：自由文本（playstyle 续行）
        if current_section == "playstyle":
            if bd.playstyle:
                bd.playstyle += "\n"
            bd.playstyle += raw.rstrip()
            continue

        # 键值对
        if current_section and "=" in line:
            key, _, value = line.partition("=")
            key = key.strip().lower()
            value = value.strip()

            if current_section == "build":
                if key == "name":
                    bd.name = value
                elif key == "background":
                    bd.background = value
                elif key == "traits":
                    bd.traits = [t.strip() for t in value.split(",") if t.strip()]
                elif key == "tags":
                    bd.tags = [t.strip() for t in value.split(",") if t.strip()]

            elif current_section == "perks":
                try:
                    order = int(key)
                except ValueError:
                    bd.parse_errors.append(f"第 {lineno} 行：序号 '{key}' 不是数字")
                    continue
                parts = [p.strip() for p in value.split(",")]
                if len(parts) < 3:
                    bd.parse_errors.append(f"第 {lineno} 行：格式应为 '序号 = 组名, 层级, 技能名'")
                    continue
                group = parts[0]
                tier = parts[1]
                perk_name = parts[2]
                bd.perks.append((order, group, tier, perk_name))

    # 按序号排序
    bd.perks.sort(key=lambda x: x[0])

    return bd


def scan_builds(builds_dir):
    """扫描 builds/ 目录下所有 .txt 文件，返回 list[BuildData]。"""
    results = []
    if not os.path.isdir(builds_dir):
        return results
    for fname in sorted(os.listdir(builds_dir)):
        if fname.lower().endswith(".txt") and not fname.startswith("."):
            path = os.path.join(builds_dir, fname)
            bd = parse_build_file(path)
            if bd:
                results.append(bd)
    return results


def generate_template(background_id, build_name, builds_dir):
    """生成一个空白流派模板文件，返回文件路径。"""
    os.makedirs(builds_dir, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_一-鿿]+", "_", build_name).strip("_")
    if not safe_name:
        safe_name = "new_build"
    filepath = os.path.join(builds_dir, f"{safe_name}.txt")

    # 不覆盖已有文件
    if os.path.exists(filepath):
        i = 2
        while os.path.exists(os.path.join(builds_dir, f"{safe_name}_{i}.txt")):
            i += 1
        filepath = os.path.join(builds_dir, f"{safe_name}_{i}.txt")

    template = f"""# {build_name}
# 流派方案文件。编辑后保存，软件自动加载。
# 空行和 # 开头的行为注释。

[build]
name = {build_name}
background = {background_id}
traits =
tags =

[perks]
# 格式：序号 = 技能树组, 层级, 技能名
# 例如：1 = Trained, Tier 2, Pathfinder
1 = , ,
2 = , ,
3 = , ,
4 = , ,
5 = , ,
6 = , ,
7 = , ,
8 = , ,
9 = , ,
10 = , ,

[playstyle]
# 在此写下流派玩法说明、装备建议、实战要点等。
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(template)
    return filepath


def create_example_file(builds_dir):
    """在 builds/ 目录创建示例文件，仅当目录为空时。"""
    os.makedirs(builds_dir, exist_ok=True)
    existing = [f for f in os.listdir(builds_dir) if f.endswith(".txt")]
    if existing:
        return None

    filepath = os.path.join(builds_dir, "示例_贵族坦克.txt")
    content = """# 贵族坦克 — 示例流派方案
# 本文件是自动生成的示例，你可以编辑或删除它。

[build]
name = 贵族坦克
background = adventurous_noble_background
traits = Athletic, Brave
tags = 坦克, 防御, 前排

[perks]
1 = Trained, Tier 2, Pathfinder
2 = Heavy Armor, Tier 1, Brawny
3 = Tactician, Tier 1, Shield Sergeant
4 = Shield, Tier 1, Shield Bash
5 = Trained, Tier 4, Death Dealer
6 = Heavy Armor, Tier 3, Forge Bound
7 = Noble, Tier 2, Rally the Troops
8 = Shield, Tier 4, Shield Wall
9 = Heavy Armor, Tier 6, Battle Forged
10 = Tactician, Tier 7, Commander's Aura

[playstyle]
以 Heavy Armor + Shield 构筑坦克前排。
Trained 提供机动与抗性，Tactician 强化团队协防。
加点优先级：先点满护甲系（Brawny → Forge Bound → Battle Forged），
再补 Shield 控制技能，最后投入 Tactician 光环。
建议搭配 Athletic 特性提升 Agile 组出现概率，或 Brave 提升 Leadership。
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath

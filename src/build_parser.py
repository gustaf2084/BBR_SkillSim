# -*- coding: utf-8 -*-
"""
build_parser.py
Parse builds/*.txt build definition files.

File format:
    [build]
    name = build name
    background = background_id
    traits = trait1, trait2  (optional)
    tags = tank, defense  (optional)

    [perks]
    1 = GroupName, Tier 3, PerkName
    2 = ...
    ...

    [playstyle]
    Free text until EOF or next [section]

Rules:
- Blank lines and lines starting with # are comments, ignored
- Section headers [xxx] are case-insensitive
- Key=value split on first =, key trimmed
- Perks section: order = group, tier, perk_name
- Encoding: UTF-8
"""

import os
import re
from i18n import t


class BuildData:
    """Data object for one build definition."""

    def __init__(self):
        self.filename = ""
        self.name = ""
        self.background = ""
        self.traits = []           # list of trait_id
        self.tags = []             # list of str
        self.perks = []            # list of (order, group, tier, perk_name)
        self.playstyle = ""
        self.parse_errors = []     # list of str

    def is_valid(self):
        return bool(self.name and self.background and self.perks)


def parse_build_file(filepath):
    """Parse a single .txt file, return BuildData or None."""
    if not os.path.isfile(filepath):
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        bd = BuildData()
        bd.filename = os.path.basename(filepath)
        bd.parse_errors.append(t("parser.read_fail") + str(e))
        return bd

    bd = BuildData()
    bd.filename = os.path.basename(filepath)
    current_section = None

    for lineno, raw in enumerate(lines, 1):
        line = raw.strip()

        # blank lines and comments
        if not line or line.startswith("#"):
            continue

        # section header
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip().lower()
            continue

        # no section: free text (playstyle continuation)
        if current_section == "playstyle":
            if bd.playstyle:
                bd.playstyle += "\n"
            bd.playstyle += raw.rstrip()
            continue

        # key=value
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
                    bd.parse_errors.append(
                        t("parser.bad_order").format(lineno, key))
                    continue
                parts = [p.strip() for p in value.split(",")]
                if len(parts) < 3:
                    bd.parse_errors.append(
                        t("parser.bad_format").format(lineno))
                    continue
                group = parts[0]
                tier = parts[1]
                perk_name = parts[2]
                bd.perks.append((order, group, tier, perk_name))

    # sort by order
    bd.perks.sort(key=lambda x: x[0])

    return bd


def scan_builds(builds_dir):
    """Scan builds/ directory for all .txt files, return list[BuildData]."""
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


def generate_template(background_id, build_name, builds_dir, lang="zh"):
    """Generate a blank build template file, return file path."""
    os.makedirs(builds_dir, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", build_name).strip("_")
    if not safe_name:
        safe_name = "new_build"
    filepath = os.path.join(builds_dir, f"{safe_name}.txt")

    # don't overwrite existing files
    if os.path.exists(filepath):
        i = 2
        while os.path.exists(os.path.join(builds_dir, f"{safe_name}_{i}.txt")):
            i += 1
        filepath = os.path.join(builds_dir, f"{safe_name}_{i}.txt")

    if lang == "en":
        template = f"""# {build_name}
# Build definition file. Edit and save — the app auto-reloads.
# Blank lines and lines starting with # are comments.

[build]
name = {build_name}
background = {background_id}
traits =
tags =

[perks]
# Format: order = Group, Tier, PerkName
# Example: 1 = Trained, Tier 2, Pathfinder
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
# Write playstyle notes, gear recommendations, battle tactics, etc. here.
"""
    else:
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


def create_example_file(builds_dir, lang="zh"):
    """Create example file in builds/ directory, only when directory is empty."""
    os.makedirs(builds_dir, exist_ok=True)
    existing = [f for f in os.listdir(builds_dir) if f.endswith(".txt")]
    if existing:
        return None

    if lang == "en":
        filepath = os.path.join(builds_dir, "Example_NobleTank.txt")
        content = """# Noble Tank — example build
# This file is auto-generated as an example. You can edit or delete it.

[build]
name = Noble Tank
background = adventurous_noble_background
traits = Athletic, Brave
tags = Tank, Defense, Frontline

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
Frontline tank built around Heavy Armor + Shield.
Trained provides mobility and resistances, Tactician strengthens team defense.
Priority: max armor line (Brawny > Forge Bound > Battle Forged),
then Shield control skills, finally Tactician aura.
Athletic trait recommended to boost Agile group, or Brave for Leadership.
"""
    else:
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

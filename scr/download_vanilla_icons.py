# -*- coding: utf-8 -*-
"""
download_vanilla_icons.py
从 Battle Brothers Fandom Wiki 下载原版技能图标，保存为 perk_{name}.png。
运行方式：python download_vanilla_icons.py
输出目录：bb skill icon/
"""

import urllib.request
import os
import sys

# Wiki Perk_XX → 英文名 + URL 路径映射
PERKS = {
    "01": ("dodge",              "6/62"),
    "03": ("crippling_strikes",  "5/50"),
    "04": ("pathfinder",         "4/44"),
    "05": ("bullseye",           "0/0a"),
    "06": ("colossus",           "a/a0"),
    "07": ("nine_lives",         "f/f8"),
    "08": ("battle_forged",      "c/c9"),
    "09": ("berserk",            "9/95"),
    "10": ("brawny",             "1/1b"),
    "11": ("rotation",           "c/c8"),
    "15": ("recover",            "4/4b"),
    "16": ("steel_brow",         "9/9d"),
    "17": ("quick_hands",        "b/bb"),
    "19": ("gifted",             "b/bb"),
    "20": ("bags_and_belts",     "7/7d"),
    "21": ("shield_expert",      "e/ed"),
    "23": ("spear_mastery",      "d/da"),
    "25": ("axe_mastery",        "9/98"),
    "26": ("flail_mastery",      "9/92"),
    "27": ("sword_mastery",      "5/56"),
    "29": ("cleaver_mastery",    "2/27"),
    "30": ("hammer_mastery",     "4/4f"),
    "33": ("mace_mastery",       "e/e7"),
    "35": ("dagger_mastery",     "9/9a"),
    "36": ("polearm_mastery",    "1/14"),
    "37": ("crossbow_mastery",   "a/a2"),
    "38": ("bow_mastery",        "d/d7"),
    "39": ("head_hunter",        "c/c2"),
    "40": ("anticipation",       "7/79"),
    "41": ("underdog",           "9/94"),
    "42": ("lone_wolf",          "a/a3"),
    "43": ("nimble",             "9/98"),
    "44": ("duelist",            "f/f8"),
    "45": ("killing_frenzy",     "0/00"),
    "46": ("fearsome",           "a/a8"),
    "47": ("indomitable",        "c/c1"),
    "48": ("adrenaline",         "6/6f"),
    "49": ("fortified_mind",     "9/9e"),
    "50": ("rally_the_troops",   "0/03"),
    "51": ("taunt",              "0/0b"),
    "52": ("relentless",         "1/1c"),
    "53": ("overwhelm",          "7/73"),
    "54": ("reach_advantage",    "0/01"),
    "56": ("footwork",           "4/44"),
    "57": ("hold_out",           "8/8d"),
    "58": ("backstabber",        "d/d7"),
    "59": ("fast_adaptation",    "f/f3"),
    "60": ("executioner",        "c/c3"),
    "61": ("student",            "9/9b"),
    "62": ("resilient",          "9/99"),
}

BASE_URL = "https://static.wikia.nocookie.net/battlebrothers/images/{path}/Perk_{num}.png/revision/latest?format=original"

def main():
    # 从脚本所在目录找 bb skill icon 文件夹
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "bb skill icon")
    os.makedirs(out_dir, exist_ok=True)

    ok = 0
    fail = 0
    skip = 0

    for num, (name, path) in sorted(PERKS.items(), key=lambda x: int(x[0])):
        out_name = f"perk_{name}.png"
        out_path = os.path.join(out_dir, out_name)

        if os.path.exists(out_path):
            print(f"[SKIP] {out_name} 已存在")
            skip += 1
            continue

        url = BASE_URL.format(path=path, num=num)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            if len(data) < 500:
                print(f"[FAIL] {out_name} ← {url} (太小: {len(data)} bytes)")
                fail += 1
                continue
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"[ OK ] {out_name} ← Perk_{num} ({len(data)} bytes)")
            ok += 1
        except Exception as e:
            print(f"[FAIL] {out_name} ← {url}")
            print(f"       {e}")
            fail += 1

    print(f"\n完成：成功 {ok}，失败 {fail}，跳过 {skip}，共 {len(PERKS)}")

if __name__ == "__main__":
    main()

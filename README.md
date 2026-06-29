# BBR_SkillSim — 战场兄弟重铸背景和技能概率模拟器

Battle Brothers Reforged 模组的角色 build 概率分析工具。输入背景和特性，正向推演各技能树组出现概率，或反向推导达到指定技能树组的最佳组合。

## 功能

- **正向模拟** — 选背景 + 特性，计算所有技能树组的出现概率分布
- **反向推导** — 选目标技能树组，找出最佳背景+特性组合
- **流派推荐** — 浏览各背景的高概率技能树组参考
- **技能树可视化** — 7 阶矩阵展示每个组的 perk 树，带图标和中文描述

## 运行环境

Windows 10/11，无需安装 Python。直接运行 `release/BBR_SkillSimulator.exe`。

## 项目结构

```
BBR_SkillSim/
├── release/             # 打包好的 Windows exe（不上传 GitHub，用 Releases 分发）
└── src/                 # 源代码
    ├── main.py          # 入口
    ├── main_window.py   # 主窗口
    ├── engine.py        # 概率引擎
    ├── data_loader.py   # 数据加载
    ├── data.json        # 结构化数据（背景/特性/技能树组）
    ├── icon_provider.py # 图标加载
    ├── skill_tree_widget.py  # 技能树矩阵可视化
    ├── perk_zh.py       # 技能中文翻译
    ├── tab_forward.py   # 正向模拟页
    ├── tab_reverse.py   # 反向推导页
    ├── tab_builds.py    # 流派推荐页
    ├── tab_about.py     # 关于页
    ├── build_safe.spec  # PyInstaller 打包配置
    ├── build_simple.bat # 一键打包脚本
    └── docs/            # 开发文档
```

## 打包

```cmd
cd src
python -m PyInstaller build_safe.spec --noconfirm
```

输出 exe 在 `src/dist/BBR_SkillSimulator.exe`，连同 `data.json` 和 `icons/` 一起放入 `release/` 分发。

## 数据来源

基于 Battle Brothers Reforged 0.7.6 模组数据解析生成，技能图标来自原版 BB Wiki 和 Reforged 模组资源。

## License

仅供个人学习和模组研究使用。

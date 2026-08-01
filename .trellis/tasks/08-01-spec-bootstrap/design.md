# 设计:BBR_SkillSim spec 结构重塑

## 目标 spec 树

```
.trellis/spec/
├── model/
│   ├── index.md              # 导航 + Pre-Development Checklist + Quality Check
│   ├── engine.md             # 概率引擎约定
│   ├── data.md               # 数据加载/路径约定
│   ├── error-handling.md     # 错误与校验
│   └── quality.md            # 质量闸门命令与禁区
├── view/
│   ├── index.md              # 导航 + 检查清单
│   ├── theme.md              # 颜色/样式唯一来源
│   ├── i18n.md               # 双语集中字典
│   ├── widgets.md            # 自定义控件与 Qt 坑
│   └── app-structure.md      # 主窗口/tab/版本
└── guides/
    ├── index.md              # 更新
    ├── code-reuse-thinking-guide.md   # 保留标题,填项目实例
    └── cross-layer-thinking-guide.md  # 保留标题,填项目实例
```

`backend/` 整体删除(database-guidelines/logging-guidelines 不适用;目录结构/质量等内容按主题吸收进 model/)。

## 每文件主题与素材来源

### model/

| 文件 | 主题 | 素材来源 |
|---|---|---|
| `index.md` | 目录导航;开发前检查清单;质量检查清单 | 本文档文件集;CLAUDE.md Commands |
| `engine.md` | 权重合成机制;analytic/MC 双模式及一致性;分数 roll 语义;Exclusive 组覆盖规则;reverse 推导两阶段剪枝;**6 实例级缓存非线程安全契约**(worker 自建引擎,`SkillEngine(engine.gd)`);缓存返回值禁止外部修改 | `src/engine.py`、`tab_reverse.py` ReverseDeriveWorker、`tests/test_engine.py`、CLAUDE.md Model layer |
| `data.md` | GameData 加载后只读可共享;双语访问器 `bg_name/trait_name/group_name`;settings.json 持久化;DUPLICATE_BG_GROUPS/HIDDEN_BACKGROUNDS → filtered_complete_backgrounds(UI 92/99);app_paths 的 exe 相邻优先/_MEIPASS 兜底;settings/builds 永远写 exe 相邻;perk_trees.json 仅 UI 懒加载,引擎不读 | `src/data_loader.py`、`src/app_paths.py`、CLAUDE.md |
| `error-handling.md` | data.json 校验失败行为;加载错误向 UI 的传播路径;build_parser 解析容错;缺失文件降级(perk_i18n 缺失等) | `src/data_loader.py`、`src/build_parser.py`、`src/main.py`(实际读取后确定) |
| `quality.md` | ruff/mypy/pytest 命令与 CI 闸门;mypy 零错误;概率显示 `f"{p*100:.1f}%"`(禁用 int 截断);单字母变量遮蔽 `t()` 历史(F821/F402);长文件编辑后验证尾部+ruff+pytest | CLAUDE.md Commands/Pitfalls、`conftest.py`、`tests/` |

### view/

| 文件 | 主题 | 素材来源 |
|---|---|---|
| `index.md` | 导航 + 检查清单 + retheme 检查点 | 本文档文件集 |
| `theme.md` | theme.py 单一颜色来源(禁颜色字面量);build_qss 运行时生成;objectName 契约(dev doc §5.2);setObjectName+选择器而非内联 setStyleSheet;代码内颜色(QPainter/表格/富文本)需 retheme() 重绘;QSS 子控件规则覆盖 ID 选择器;QScrollArea 暗色 viewport 检查 | CLAUDE.md Cross-cutting、`src/theme.py`、`src/docs/开发文档.md` §5.2 |
| `i18n.md` | i18n.py 集中字典 `t(key)`/`set_lang()`;禁硬编码用户可见字符串;tab 的 retranslate + 语言切换重调 on_data_ready();perk_i18n.json + perk_zh.py | CLAUDE.md Cross-cutting、`src/i18n.py`、`src/perk_zh.py` |
| `widgets.md` | skill_tree_widget:7 层 × N 组矩阵、概率弧线(QPainter 绘制)、ColumnHeaderOverlay 子控件(Qt6 drawForeground 裁剪不可靠);QCompleter 需显式 QStringListModel;暗色主题容器检查 | `src/skill_tree_widget.py`、CLAUDE.md Pitfalls |
| `app-structure.md` | main_window:QListWidget + QStackedWidget 导航、四 tab 职责、Ctrl+1-4;VERSION 根文件唯一版本源;reverse 在 QThread worker、forward 主线程同步 | `src/main_window.py`、各 tab、CLAUDE.md View layer |

### guides/

| 文件 | 动作 |
|---|---|
| `code-reuse-thinking-guide.md` | 保留现有通用框架,新增"本项目复用点"小节:reverse 纯度排序复用 forward_simulate 命中缓存;analytic/MC 共享权重合成路径;ui_components 复用;perk_zh 包装层;双语访问器避免直接读 dict |
| `cross-layer-thinking-guide.md` | 新增项目场景:model→view 数据流(引擎结果不可变传给 UI);线程边界(worker 自建引擎);retheme/i18n 跨层联动(数据变化重调 on_data_ready);perk_trees.json 不参与概率计算 |

## 写作约定

- 全部中文;代码标识符/命令/文件路径保留原文
- 每条规范格式:适用时机 → 本地模式 → 证据(文件:符号)→ 反模式/常见错误
- 短代码片段仅在有助于说明时使用,优先引用 `文件路径` + 符号名
- 引用 CLAUDE.md 内容时按本任务范围重写,不复制大段原文
- 删除模板遗留:所有 "To fill"/"TBD"/模板说明文字

## 验证方案

1. `grep -R "To be filled\|TODO: fill\|placeholder\|TBD" .trellis/spec` 无命中
2. `find .trellis/spec -type f` 与各 index.md 链接一致
3. `git status` 确认仅 .trellis/ 变更
4. 快速 `ruff check src tests` + `pytest -q` 确认基线未破坏(规范不改代码,预期通过)

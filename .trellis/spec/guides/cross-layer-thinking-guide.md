# 跨层数据流思考指南(BBR_SkillSim)

> **目的**:实现前想清楚 model → view 之间的数据流、线程边界与契约。

---

## 项目分层

```
data.json ─→ data_loader.load_data() ─→ GameData(只读,可跨线程共享)
                │
                ├─→ SkillEngine(每线程自建,缓存非线程安全)
                │       ├─ analytic / Monte Carlo 双模式
                │       ├─ forward_simulate() / reverse_derive()
                │       └─ 结果 dict(共享对象,禁止外部修改)
                │
                └─→ on_data_ready(gd, engine, icon_provider) → 四个 tab 的 UI 状态
```

## 层间契约(关键边界)

### 1. 数据边界:GameData 只读

- 所有线程共享同一个 `GameData`,加载后不可变
- 引擎、worker、UI 都不修改它(见 [../model/data.md](../model/data.md))
- **故障点**:某处 `gd._data[...] = ...` 或就地改 dict —— 会污染所有线程的视图

### 2. 线程边界:引擎归属

- UI 主线程:正向模拟(亚秒级)
- `ReverseDeriveWorker(QThread)`(`tab_reverse.py:41`):逆向推导,**自建** `SkillEngine(engine.gd)`(`:54`)
- 引擎缓存是实例级的,绝不让两个线程共享同一引擎实例(见 [../model/engine.md](../model/engine.md))
- 取消契约:worker 支持逐组合取消(`cancelled` signal、`isInterruptionRequested`)

### 3. 就绪/语言切换联动

数据 tab 实现统一签名 `on_data_ready(gd, engine, icon_provider)`(`tab_forward.py:340` 等):

- 数据就绪时调用一次
- **语言切换时也调用** —— 数据驱动文本(背景/特性/组名)来自 `GameData` 访问器,必须重刷
- 静态文本走各 tab 的 `retranslate()`(`tab_forward.py:376` 等)
- **故障点**:新 tab 忘了实现 `on_data_ready`,或语言切换只调 `retranslate()` 不重刷数据文本 → 切换语言后名称残留旧语言

### 4. 主题联动

代码内颜色(QPainter/表格/富文本)不随 QSS 刷新,必须由 `retheme()` 重绘(`tab_forward.py:428` 等)。新增代码内颜色时同步扩展 `retheme()`(见 [../view/theme.md](../view/theme.md))。

### 5. 版本边界

`VERSION`(根文件)是唯一版本源:`main_window.py:39`(`_read_version()`)经 `resolve_resource("VERSION", include_project_root=True)` 读取;CI 用 git tag 覆盖;exe 相邻优先、`_MEIPASS` 兜底。不要在 UI 里散落版本常量。

### 6. UI-only 数据边界

`perk_trees.json` 只被 UI 消费(懒加载),**引擎从不读** —— perk 树改动不可能影响概率结果。怀疑"perk 树导致概率不对"时先查方向:引擎只吃 `data.json`。

## 跨层改动的检查清单

改一处影响多层的代码前:

- [ ] 映射完整数据流:改动是否穿过 GameData → engine → tab 任一边界?
- [ ] 线程归属:新计算在哪个线程跑?引擎实例是那个线程自己建的?
- [ ] 结果对象:是否修改了引擎返回的共享 dict?(禁止)
- [ ] 联动钩子:新 UI 文本/颜色挂进 `retranslate()`/`retheme()`/`on_data_ready` 了吗?
- [ ] 语言/主题切换后验证:切 en 无残留中文、切 dark 无残留浅色块
- [ ] 错误传播:加载失败走 `DataError` → 错误页 → 全局 `excepthook`(`main.py:57`),UI 层不吞异常细节

## 反模式速查

- 两个线程共享同一 `SkillEngine`
- UI 线程同步调用 `reverse_derive()`
- 修改引擎返回的缓存 dict
- 语言切换只 `retranslate()` 不重刷数据文本
- 新控件颜色绕过 `theme.py`(QSS 刷新不到,QPainter 色不跟随主题)

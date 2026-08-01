# 应用结构与主窗口规范(main_window / tabs)

适用时机:修改 `src/main_window.py`、任一 tab 文件,或新增页面/入口。

## 导航结构

`MainWindow(QMainWindow)`(`main_window.py:69`):

- 左侧导航 `QListWidget`(`self.nav`,`:257`)+ 右侧 `QStackedWidget`(`self.stack`,`:294`)承载四个 tab
- 导航项文本走 `t(key)`(`:262`);快捷键 `Ctrl+1..4` 在 `_setup_shortcuts()`(`:379`)注册
- 新增页面:在 stack 里加 tab + 导航项 + 快捷键,并同步 `retranslate()`(导航文本也是 i18n)

## 四个 tab 的职责与协作约定

| Tab | 职责 | 数据入口 |
|---|---|---|
| `tab_forward.py` | 正向模拟:背景+特性 → 各组出现概率(主线程同步,亚秒级,带 busy 态) | `on_data_ready(gd, engine, icon_provider)`(`:340`) |
| `tab_reverse.py` | 逆向推导:目标组 → 最佳背景/特性组合(QThread worker) | `on_data_ready`(`:253`);`ReverseDeriveWorker(QThread)`(`:41`) |
| `tab_builds.py` | 配装推荐 | `on_data_ready`(`:296`) |
| `tab_about.py` | 关于页(无数据依赖) | `retranslate`/`retheme` 即可 |

- 三个数据 tab 都实现 `on_data_ready(gd, engine, icon_provider)`:数据就绪与语言切换时都会被调用,签名一致
- **线程边界**:逆向推导在 `ReverseDeriveWorker` 里跑,worker **自建** `SkillEngine(engine.gd)`(`tab_reverse.py:54`),支持逐组合取消(`cancelled` signal `:45`、`isInterruptionRequested` `:78`);正向模拟快,留在主线程。不要把 `reverse_derive()` 丢主线程,也不要把共享引擎塞进 worker(见 [../model/engine.md](../model/engine.md))

## 版本号

- `VERSION`(仓库根,单行文本)是唯一版本源;`main_window.py:39`(`_read_version()`)用 `resolve_resource("VERSION", include_project_root=True)` 读取,失败回退 `'dev'`
- CI 构建时用 git tag 覆盖 `VERSION`;改动版本只改这个文件,不散落常量

## 启动流程(main.py)

1. 高 DPI 策略设置(`PassThrough`,`main.py:45`)
2. 先读 `settings.json` 的主题偏好再建 UI(`set_theme`,`:53`),拼接 `build_qss() + 用户 style.qss 覆盖`
3. 全局异常钩子弹 QMessageBox(`:57`)
4. 懒导入 `MainWindow` 避免数据加载失败时卡在异常页(`:68`)

## 反模式汇总

- 在 tab 内直接 `QThread` 裸跑逻辑而不走 worker 模式(缺少取消与进度信号)
- 把 `main_window.py` 的导航/栈结构改写成每个 tab 自建窗口 —— 语言/主题联动依赖统一入口
- UI 线程里同步调用重型引擎接口(正向外可,逆向不行)

## 参考

- 根 `CLAUDE.md` View layer 节;启动细节 `src/main.py`;权威手册 `src/docs/开发文档.md`

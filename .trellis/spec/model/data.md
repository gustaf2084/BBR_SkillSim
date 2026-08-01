# 数据层规范(data_loader / app_paths)

适用时机:修改 `src/data_loader.py`、`src/app_paths.py`,或新增需要读取/写入数据文件的代码。

## GameData 只读契约

`load_data()`(`data_loader.py:288`)校验并构造 `GameData`(`data_loader.py:95`),**加载后不可变**,是唯一可安全跨线程共享的对象:

- 引擎、UI、工作线程共用同一个 `GameData`,绝不在加载后修改它
- 数据访问走属性访问器(`meta`/`config`/`backgrounds`/`traits`/`groups`/`exclusive_groups`/`attribute_weights`/`projected_attributes`/`builds` 等,`data_loader.py:113-158`),不直接摸私有 `_data`
- `perk_trees`(`data_loader.py:140`)是懒加载的(`_load_perk_trees_file`,仅 UI 使用 —— 引擎从不读 perk 树数据,perk 树改动不可能影响概率结果)

## 双语访问器

显示名称一律通过 `GameData` 访问器,跟随 `set_lang()`(`data_loader.py:160`)切换:

- `bg_name(bg_id)`(`data_loader.py:220`)、`trait_name(trait_id)`(`:225`)、`group_name(group_id)`(`:230`)
- 反模式:直接从 `backgrounds` dict 里取原始 name 字段拼进 UI —— 语言切换后不会更新,且可能与 `GameData` 内部显示名逻辑(含剔除逻辑)不一致

## UI 背景隐藏(引擎仍见全部)

`DUPLICATE_BG_GROUPS`(`data_loader.py:32`)与 `HIDDEN_BACKGROUNDS`(`:36`)→ `_build_excluded()` → `filtered_complete_backgrounds()`(`:242`):UI 展示 92/99 个背景,但**引擎照常计算全部背景**。给 UI 加背景列表过滤时用 `filtered_complete_backgrounds()`,不要改 `complete_backgrounds()`(`:238`)或引擎侧逻辑。

## settings.json 持久化

`SETTINGS_FILE = "settings.json"`(`data_loader.py:54`)、`_load_settings()`(`:58`)/`_save_settings()`(`:72`)负责读写,失败只记 `_logger.warning` 不崩溃:

- 写入目录一律用 `app_paths.external_app_dir()`(exe 相邻;打包后 `_MEIPASS` 只读,禁止写入)
- 反模式:手写 `os.path.join(os.path.dirname(sys.executable), ...)` 或把设置写进 `_MEIPASS`
- 顶层非对象、损坏 JSON 都应被容忍并降级(日志警告),不能让应用启动失败

## 应用路径规则(app_paths)

`src/app_paths.py` 是唯一的路径权威:

- `external_app_dir()`:`sys.frozen` 时为 exe 目录,否则脚本目录 —— 用户可写、可覆盖资源
- `bundled_app_dir()`:打包时 `sys._MEIPASS` —— 只读分发资源
- `resolve_resource(filename, include_project_root=...)`(`app_paths.py:44`):外置优先 → 内置兜底 →(可选)项目根;全部缺失时返回外置候选
- 数据文件(`data.json`、`perk_trees.json`、`perk_i18n.json`、`VERSION`)读取用 `resolve_resource()`;`settings.json` 与 `builds/` 永远写 exe 相邻
- 反模式:在别处重复实现 `_MEIPASS` 探测或硬编码 `sys.executable` 拼接

## 参考

- 加载校验错误处理:见 [error-handling.md](./error-handling.md)
- 打包行为:根 `CLAUDE.md` PyInstaller 路径规则节;测试:`tests/test_app_paths.py`、`tests/test_data_loader.py`

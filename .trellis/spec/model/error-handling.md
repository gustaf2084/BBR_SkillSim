# 错误处理与数据校验规范

适用时机:修改数据加载、解析逻辑,或新增会失败的 I/O 路径。

## 异常类型与语义

`DataError`(`data_loader.py:14`)是数据加载的专用异常,带 `code` 字段分类:

| code | 触发场景 |
|---|---|
| `missing` | data.json 不存在 |
| `format` | JSON 解析失败 / 读取异常 |
| `schema` | 顶层必需键缺失(`TOP_KEYS`) |
| `version` | 版本不匹配且 `strict_version=True` |
| `incomplete` | `strict=True` 且存在缺失字段/悬空引用 |

`IconError`(`data_loader.py:21`)用于图标资源相关错误。新增加载失败场景时优先扩展既有 code 语义,不要发明平行的异常类。

## 宽容加载(默认)

`load_data()`(`data_loader.py:288`)默认 `strict=False`:

- 背景/特性缺字段、组引用悬空 ⇒ 只进 `warnings` 列表,不抛异常
- 版本不匹配默认**抛出**(`strict_version=True`);确需兼容旧数据时才显式传 `strict_version=False` 降级
- 反模式:给生产调用加 `strict=True` 当"严格校验开关" —— 那会让缺失字段的应用直接启动失败,与产品"宽容加载"行为相悖;`strict=True` 的语义是校验器专用

## 缺失资源的降级链

- `load_perk_trees()`(`data_loader.py:341`):`perk_trees.json` 不存在 → 回退读取 `data.json` 内嵌的 `perk_trees` → 再不存在返回 `{}`。缺失场景三层降级不抛;`GameData` 的懒加载路径 `_load_perk_trees_file()`(`data_loader.py:145`)则对损坏 JSON 也容错(记 warnings 并回退内嵌数据)
- `perk_i18n.json` 缺失/损坏:UI 层应降级(回退英文或原始文本),不得因翻译缺失崩溃
- 用户自定义 `style.qss`(`main.py:31` `load_user_qss_override`):读失败静默忽略,返回空串

## 向 UI 传播

- 加载失败在 `MainWindow(data_path=...)` 内处理并呈现错误页;`main.py:68` 用懒导入避免加载阻塞时先卡在异常页
- 全局兜底:`main.py:57` `global_excepthook` 把未捕获异常弹 `QMessageBox`(标题/正文走 `t("error.global_title")` 等 i18n 键),异常消息截断 800 字符
- settings.json 读写失败只记 `_logger.warning`(`data_loader.py:68/86`),绝不阻止应用启动 —— 本项目唯一的 logging 使用点也在这里

## 反模式汇总

- 在 `load_data` 外面再包一层 try/except 把所有异常吞掉 —— 丢失 `DataError.code` 信息
- 给 UI 报错直接拼英文/中文原始串,不通过 `i18n.t()`(见 [../view/i18n.md](../view/i18n.md))
- 手写文件存在性判断(`os.path.exists`)代替 `resolve_resource()` 的候选链

## 参考

- 校验细节:`tests/test_data_loader.py`;启动流程:`src/main.py`

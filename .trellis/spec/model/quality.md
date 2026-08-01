# 质量闸门与代码禁区

适用时机:任何提交前;尤其修改 `engine.py`、`data_loader.py` 等长文件后。

## 质量闸门命令(CI 强制)

从项目根目录执行(本地 venv 为 `.venv`,必要时用 `.venv/Scripts/python`):

```bash
ruff check src tests              # lint —— CI 闸门,必须零告警
python -m mypy src                # 类型检查 —— CI 闸门,必须零错误
python -m pytest tests/ -q        # 全量测试(engine + data loader)
```

CI(`.github/workflows/test.yml`)在每次 push/PR 跑 ruff + pytest(Python 3.10 & 3.12);mypy 零错误是硬性要求。测试从根目录跑:`conftest.py` 把 `src/` 放进 `sys.path`,测试直接 `import engine`(tests 内有 E402 per-file ignore)。

## 概率显示格式(强制)

概率值一律 `f"{p*100:.1f}%"` —— int 截断会丢失边界值(99.7% → 99%)。搜索 `int(` 与概率相乘的写法时留意此坑。此规则同样约束 UI 层,源头在模型层结果输出。

## 历史禁区(项目教训)

- **单字母循环变量**(`t`、`c`):多次遮蔽过 `i18n.t()` 导入或破坏列表推导(ruff F821/F402 会抓住)。不要用单字母变量名
- **长文件编辑后截尾**:`engine.py`(1239 行)、`main_window.py` 等长文件历史上被旧工具截断过文件尾部。编辑后必须:确认文件末尾完整 → `ruff check` → pytest
- **缓存返回对象被修改**:engine 缓存返回的 dict 是共享对象,调用方修改会污染后续命中(见 [engine.md](./engine.md) 线程安全契约)

## 新增逻辑的检查顺序

1. 先确认是否已有实现(缓存、`forward_simulate()` 复用、`GameData` 访问器)—— 见 [../guides/code-reuse-thinking-guide.md](../guides/code-reuse-thinking-guide.md)
2. 行为变更同步 `src/docs/开发文档.md`(权威开发手册兼 changelog,`版本历史` 节是唯一 changelog 源)
3. 新权重/概率逻辑必须在 `tests/test_engine.py` 补 analytic/MC 对照用例
4. 提交信息遵循仓库惯例(中文;`push_github.bat` 或 `git push_github` 流程,禁止 force-push)

## 参考

- 命令细节与运行方式:根 `CLAUDE.md` Commands 节
- 测试约定:`conftest.py`、`tests/test_engine.py`(fractional 等关键用例用 `-k` 可单跑)

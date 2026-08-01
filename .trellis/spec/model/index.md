# 模型层开发规范(非 UI 逻辑)

> 适用范围:`src/` 中不依赖 Qt 的模块 —— `engine.py`、`data_loader.py`、`app_paths.py`、`build_parser.py`、`perk_zh.py`。UI 层规范见 [`../view/index.md`](../view/index.md)。

## 文件索引

| 指南 | 内容 |
|------|------|
| [engine.md](./engine.md) | SkillEngine 概率核心:权重合成、双计算模式、缓存与线程安全契约 |
| [data.md](./data.md) | GameData 只读契约、双语访问器、settings 持久化、app_paths 路径规则 |
| [error-handling.md](./error-handling.md) | 数据校验、加载失败处理、异常类型 |
| [quality.md](./quality.md) | 质量闸门命令、mypy 零错误、概率显示格式、历史禁区 |

## Pre-Development Checklist(改模型层代码前)

- [ ] 明确了计算模式语义:analytic(无放回递归,非 `1-(1-p)^n`)与 Monte Carlo(整角色联合模拟)的结果必须一致(`tests/test_engine.py` 有对照用例)
- [ ] 确认不会触碰 `SkillEngine` 实例级缓存,或已理解缓存契约(见 [engine.md](./engine.md) 线程安全节)
- [ ] 新增用户可见字符串已走 `i18n.t()`/`GameData` 双语访问器,未硬编码
- [ ] 数据相关改动确认了只读契约:`GameData` 加载后不可变,可跨线程共享
- [ ] 路径相关改动使用 `app_paths.py` 的 `resolve_resource()`/`external_app_dir()`,未手写 `_MEIPASS` 判断

## Quality Check(模型层改动后)

- [ ] `ruff check src tests` 无告警(F821/F402 尤其注意单字母变量)
- [ ] `python -m mypy src` 零错误(CI 闸门)
- [ ] `python -m pytest tests/ -q` 全绿(engine + data loader 用例)
- [ ] 概率值显示格式统一为 `f"{p*100:.1f}%"`(禁止 int 截断)
- [ ] 长文件(`engine.py` 1239 行)编辑后确认文件尾部完整

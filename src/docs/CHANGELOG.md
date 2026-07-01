# Changelog

## v0.1.0 (2026-07-01)

### 新增
- 导出功能：正向/反向结果表支持「复制文本」和「导出 CSV」
- 搜索筛选：特性网格和目标组面板支持搜索输入框
- GitHub Actions CI：推送 `v*` 标签自动构建 Windows EXE
- 反向推导进度条 + 取消按钮（QThread 异步执行）
- 单元测试：90 个测试覆盖引擎和数据加载

### 优化
- 引擎缓存：正向 LRU（容量 200）+ 无放回子结果缓存（修复跨配置碰撞 bug）
- 反向推导两阶段剪枝：约 10x 速度提升
- perk 翻译 JSON 化：158 条从硬编码迁移到 `perk_i18n.json`
- 技能树数据懒加载：`perk_trees.json` 从 data.json 分离
- EXE 体积缩小：排除 QtWebEngine/QtQuick/Qt3D 等大型未使用模块
- 窗口状态持久化：关闭时保存位置/大小/标签页，启动时恢复
- 版本号集中化：单一 VERSION 文件，CI 从 git tag 注入

### 修复
- `_setup_shortcuts()` 快捷键注册从未被调用
- `build_simple.bat` 编码乱码
- `_norepl_cache` 不同背景/特性配置下的缓存碰撞
- 反向推导多目标时 NameError：`_finish_derive` 列表推导式变量名 `c` 应为 `cb`（触发条件：多目标且有结果时）

### 开发
- 类型注解：engine.py + data_loader.py 完整类型标注
- 代码规范：ruff + mypy + pytest 配置
- 依赖管理：requirements.txt + requirements-dev.txt
- 文档：README 用户指南 + FAQ + 开发者文档

## v0.0.3 (2026-06-29)

### 新增
- 正向模拟：解析近似 + 蒙特卡洛双模式
- 反向推导：目标组 → 最佳背景+特性组合
- 流派推荐：自动分析 + 自定义流派文件
- 技能树可视化：7 阶矩阵，中英文切换
- 6 类别分组体系：Shared / Exclusive / Weapon / Armor / Fighting Style / Special

### 数据
- 基于 Battle Brothers Reforged 0.7.6 模组数据

## v0.0.1-v0.0.2

- 初始原型：基础概率引擎 + PySide6 GUI

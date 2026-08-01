# 执行计划:BBR_SkillSim spec 结构重塑

## 实施清单

- [ ] 1. 调研确认(写文档前):读 `src/engine.py` 关键函数签名、`data_loader.py` 的 GameData/校验路径、`theme.py` 的 LIGHT/DARK 与 build_qss、`i18n.py` 的 t/set_lang、`main_window.py` 导航结构、`skill_tree_widget.py` 弧线绘制、`tab_reverse.py` ReverseDeriveWorker —— 只读,确保每条规范有真实证据
- [ ] 2. 创建 `.trellis/spec/model/`,写 5 个文件(index/engine/data/error-handling/quality)
- [ ] 3. 创建 `.trellis/spec/view/`,写 5 个文件(index/theme/i18n/widgets/app-structure)
- [ ] 4. 更新 `.trellis/spec/guides/` 3 个文件(两个 guide 填项目实例,index 同步)
- [ ] 5. 删除 `.trellis/spec/backend/` 整个目录
- [ ] 6. 验证:
  - [ ] `grep -R "To be filled\|TODO: fill\|placeholder\|TBD" .trellis/spec` 无命中
  - [ ] 各 index.md 链接与文件集一致
  - [ ] `git status` 仅 .trellis/ 变更
  - [ ] `ruff check src tests` 通过、`python -m pytest tests/ -q` 通过(基线确认)

## 质量闸门

- 每写 1 个目录(模型层、视图层、guides)后自查:证据是否真实(读过对应源码)、无占位文本、语言中文
- 全部完成后跑验证清单 6 全部项

## 回滚点

- 写文档阶段:直接编辑/删除 `.trellis/spec/` 文件即可回滚
- `backend/` 删除前确认 model/ + view/ 已就位;若需恢复,内容已在 design.md 中映射(模板内容本身无价值)
- 产品代码零改动,无代码回滚需求

## 验收映射

对应 prd.md 验收标准 6 条,验证清单 6 全绿即为完成。

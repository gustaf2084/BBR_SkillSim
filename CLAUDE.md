# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BBR_SkillSim is a Windows desktop app (Python 3.10+ / PySide6) that computes perk-tree probabilities for the Battle Brothers Reforged mod: forward simulation (background + traits → per-group appearance probabilities), reverse derivation (target groups → best background/trait combos), and build recommendations. Pure local app, no network.

The project language is Chinese: UI copy, comments, docs, and commit messages are predominantly zh (the runtime UI is bilingual zh/en). **`src/docs/开发文档.md` is the authoritative developer manual and changelog** — its 版本历史 section is the single changelog source. Keep it and README.md in sync with meaningful changes.

## Commands

Local venv is `.venv` (Python 3.12); use `.venv/Scripts/python` if plain `python` lacks PySide6. From the project root:

```bash
pip install -r requirements-dev.txt              # PySide6 + pytest/ruff/mypy/pyinstaller

python -m pytest tests/ -q                       # all tests (engine + data loader)
python -m pytest tests/test_engine.py -k fractional -v   # single file / pattern

ruff check src tests                             # lint — CI gate, must be clean
```

- **Run the app**: `cd src && python main.py` (must run from `src/`; data.json is located relative to the script).
- **Build exe** (Windows only): `cd src && python -m PyInstaller build_safe.spec --noconfirm` — use `python -m PyInstaller`, not bare `pyinstaller` (PATH issues). Or run `src\build_simple.bat`. The output `src/dist/BBR_SkillSimulator.exe` needs `data.json`, `perk_trees.json`, `perk_i18n.json`, and `icons/` beside it.
- **Push**: `push_github.bat [message]` — add → commit → push; never force-pushes.
- **CI**: `test.yml` runs ruff + pytest on every push/PR (Python 3.10 & 3.12); `build.yml` builds the exe on `v*` tags, overwriting `VERSION` from the tag.
- mypy is configured but **not** a CI gate — 13 legacy errors exist in engine/data_loader/i18n; don't add new ones.

Root `conftest.py` puts `src/` on `sys.path`, so tests import modules directly (`import engine`); `tests/*` has a ruff per-file ignore for E402.

## Architecture

### Model layer

- **`data_loader.py`** — loads/validates `data.json` into `GameData` (read-only after load, safe to share across threads). Bilingual accessors `bg_name()/trait_name()/group_name()` follow `gd.lang`. Also owns `settings.json` persistence and UI-only background hiding: `DUPLICATE_BG_GROUPS` + `HIDDEN_BACKGROUNDS` → `filtered_complete_backgrounds()` (UI shows 92 of 99 backgrounds; the engine still sees all).
- **`engine.py`** — `SkillEngine`, the probability core:
  - Weight synthesis per group: base probability × self_weight + background multipliers + trait weights + talent-star weights + projected-attribute weights + exclusive-group cascades. Any zero source removes the group; `melee_only` backgrounds zero all ranged groups. Trait weight `"+"` = strong boost (`config.big_weight` = 10.0); `"0"` = disable.
  - Two calculation modes with matching results: **analytic** (no-replacement sampling recursion with memoization — deliberately not `1-(1-p)^n`) and **Monte Carlo** (joint simulation of full characters via `_forward_monte_carlo_all`, 20000 samples, fixed seed).
  - **Fractional roll counts** (e.g. Exclusive category baseline 0.5): fraction f means "probability f of one extra roll", `P = (1-f)·P(⌊n⌋) + f·P(⌊n⌋+1)`.
  - **Guaranteed exclusive groups** (fixed/prob/mixed) *override* the normal Exclusive-category roll probability — they do not stack with it.
  - **Reverse derivation**: two-phase pruning — score all backgrounds trait-less, keep top N, expand trait combinations only for those; dedupe by background; purity (non-target-group noise) is the secondary sort and reuses `forward_simulate` to hit its cache.
- **Threading/cache contract (critical)**: `SkillEngine` holds five instance-level caches and is **not thread-safe**. Worker threads must construct their own engine over the shared read-only `GameData` — see `ReverseDeriveWorker` in `tab_reverse.py` (`SkillEngine(engine.gd)`). Dicts returned from engine caches are shared objects; callers must never mutate them.

### View layer

- **`main_window.py`** — QListWidget nav + QStackedWidget hosting four tabs (`tab_forward/tab_reverse/tab_builds/tab_about.py`); language + theme toggles; Ctrl+1–4 shortcuts; reads the root `VERSION` file.
- Reverse derivation runs in a QThread worker with progress/cancel; forward simulation runs synchronously on the main thread (sub-second) with a busy state.
- **`skill_tree_widget.py`** — QGraphicsView 7-tier × N-group perk matrix; probability halo arcs (arc length = probability) are the signature visual. Column headers are drawn by the `ColumnHeaderOverlay` child widget because Qt6 `drawForeground` clips unreliably — don't move them back into the view.

### Cross-cutting conventions (enforced)

- **`theme.py` is the single source of truth for every UI color.** LIGHT/DARK token dicts; `build_qss()` generates the entire stylesheet at runtime (no .qss file in the repo; an exe-adjacent `style.qss` is only a user override layer). Never write color literals outside `theme.py`. Style widgets via `setObjectName` + selectors in `build_qss()` (objectName contract table: dev doc §5.2), not inline `setStyleSheet`. Colors set in code (table item colors, QPainter, rich-text HTML) do not refresh with QSS — each tab's `retheme()` must repaint them; extend `retheme()` whenever adding code-set colors.
- **`i18n.py` is the centralized zh/en dictionary** (`t(key)`, `set_lang()`). No hardcoded user-facing strings. Each tab implements `retranslate()` for static text; a language switch also re-calls `on_data_ready()` for data-driven text. Perk names/descriptions live in `perk_i18n.json`, accessed through the `perk_zh.py` wrapper.
- **PyInstaller path rules**: `data.json`/`perk_trees.json`/`perk_i18n.json` are read exe-adjacent first, bundled `_MEIPASS` copy as fallback; `settings.json` and `builds/` are always written exe-adjacent — never into `_MEIPASS` (read-only).
- **`VERSION` at the repo root is the single version source** — `main_window.py` reads it, `build_safe.spec` bundles it, CI overwrites it from the git tag.
- `perk_trees.json` is UI-only and lazy-loaded; the engine never reads it, so perk-tree data changes cannot affect probability results.
- Probability display: always `f"{p*100:.1f}%"` — int truncation loses edge values (99.7% → 99%).

## Known pitfalls (from project history — dev doc §9)

- Single-letter loop variables (`t`, `c`) have repeatedly shadowed the i18n `t()` import or broken list comprehensions here; ruff (F821/F402) catches these — keep it clean and avoid single-letter names.
- Editing long files (`engine.py`, `main_window.py`, tab files) has historically truncated file tails with earlier tooling; after editing them, verify the end of the file is intact and run `ruff check` + pytest.
- Qt specifics that have bitten before: QSS sub-control rules (e.g. `QListWidget::item { color }`) override ID-selector colors; QScrollArea viewports fall back to the system (light) palette in dark theme, so new container widgets need a dark-theme check; `QCompleter` needs an explicitly created `QStringListModel`.

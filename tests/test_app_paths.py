# -*- coding: utf-8 -*-
"""PyInstaller 资源路径与外部覆盖层回归测试。"""

import importlib
import json
import os
import sys

import main_window


def _set_frozen_env(monkeypatch, external_dir, bundled_dir):
    executable = external_dir / "BBR_SkillSimulator.exe"
    executable.write_bytes(b"")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(executable))
    monkeypatch.setattr(sys, "_MEIPASS", str(bundled_dir), raising=False)


def test_resolve_resource_prefers_exe_adjacent_file(monkeypatch, tmp_path):
    external_dir = tmp_path / "external"
    bundled_dir = tmp_path / "bundled"
    external_dir.mkdir()
    bundled_dir.mkdir()
    _set_frozen_env(monkeypatch, external_dir, bundled_dir)

    external_file = external_dir / "perk_i18n.json"
    bundled_file = bundled_dir / "perk_i18n.json"
    external_file.write_text("external", encoding="utf-8")
    bundled_file.write_text("bundled", encoding="utf-8")

    from app_paths import resolve_resource

    assert resolve_resource("perk_i18n.json") == str(external_file)


def test_read_version_falls_back_to_bundled_version(monkeypatch, tmp_path):
    external_dir = tmp_path / "external"
    bundled_dir = tmp_path / "bundled"
    external_dir.mkdir()
    bundled_dir.mkdir()
    _set_frozen_env(monkeypatch, external_dir, bundled_dir)
    (bundled_dir / "VERSION").write_text("0.4.7\n", encoding="utf-8")

    assert main_window._read_version() == "0.4.7"


def test_perk_i18n_prefers_exe_adjacent_override(monkeypatch, tmp_path):
    external_dir = tmp_path / "external"
    bundled_dir = tmp_path / "bundled"
    external_dir.mkdir()
    bundled_dir.mkdir()
    _set_frozen_env(monkeypatch, external_dir, bundled_dir)

    external_data = {"Probe Perk": {"zh": "外部翻译", "desc_zh": "外部描述"}}
    bundled_data = {"Probe Perk": {"zh": "内置翻译", "desc_zh": "内置描述"}}
    (external_dir / "perk_i18n.json").write_text(
        json.dumps(external_data, ensure_ascii=False), encoding="utf-8")
    (bundled_dir / "perk_i18n.json").write_text(
        json.dumps(bundled_data, ensure_ascii=False), encoding="utf-8")

    sys.modules.pop("perk_zh", None)
    perk_zh = importlib.import_module("perk_zh")

    assert perk_zh.get_perk_name_zh("Probe Perk") == "外部翻译"
    assert perk_zh.get_perk_desc_zh("Probe Perk") == "外部描述"

    sys.modules.pop("perk_zh", None)


def test_perk_trees_falls_back_to_bundled_file(monkeypatch, tmp_path):
    external_dir = tmp_path / "external"
    bundled_dir = tmp_path / "bundled"
    external_dir.mkdir()
    bundled_dir.mkdir()
    _set_frozen_env(monkeypatch, external_dir, bundled_dir)

    source_data_path = os.path.join(os.path.dirname(__file__), "..", "src", "data.json")
    with open(source_data_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    data["perk_trees"] = {}
    external_data_path = external_dir / "data.json"
    external_data_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    bundled_trees = {"Probe": {"1": ["Probe Perk"]}}
    (bundled_dir / "perk_trees.json").write_text(
        json.dumps(bundled_trees, ensure_ascii=False), encoding="utf-8")

    from data_loader import load_data

    game_data = load_data(str(external_data_path), lazy_perk_trees=True)
    assert game_data.perk_trees == bundled_trees

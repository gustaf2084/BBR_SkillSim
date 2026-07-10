# -*- coding: utf-8 -*-
"""统一解析开发环境与 PyInstaller 环境中的应用路径。"""

import os
import sys


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def external_app_dir() -> str:
    """返回用户可写、可覆盖资源所在目录。"""
    if is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def bundled_app_dir() -> str:
    """返回随程序分发的只读资源目录。"""
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        return os.path.abspath(sys._MEIPASS)
    return os.path.dirname(os.path.abspath(__file__))


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_candidates(filename: str, *, include_project_root: bool = False) -> list[str]:
    """按外部覆盖、内置资源、项目根目录的顺序返回候选路径。"""
    directories = [external_app_dir(), bundled_app_dir()]
    if include_project_root:
        directories.append(project_root())

    candidates: list[str] = []
    for directory in directories:
        path = os.path.join(directory, filename)
        if path not in candidates:
            candidates.append(path)
    return candidates


def resolve_resource(filename: str, *, include_project_root: bool = False) -> str:
    """返回首个存在的资源路径；全部缺失时返回外部候选路径。"""
    candidates = resource_candidates(filename, include_project_root=include_project_root)
    for path in candidates:
        if os.path.isfile(path):
            return path
    return candidates[0]


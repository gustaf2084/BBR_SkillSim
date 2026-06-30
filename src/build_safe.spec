# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置（安全版 — Windows 兼容）。
与 build.spec 的区别：减少了 PySide6 子模块的排除，避免 Windows 上 Qt 平台插件
因缺少隐式依赖（QtXml/QtNetwork/QtOpenGL）导致 PyInstaller 崩溃。

用法（Windows）：
  pyinstaller build_safe.spec

说明：
  - 单文件 onefile exe
  - data.json 打包进 exe 作为兜底（用户同级目录的 data.json 优先）
  - icons 文件夹不打包，放 exe 同级目录
"""

import os

block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[
        ('data.json', '.'),
    ],
    hiddenimports=[
        'tab_forward',
        'tab_reverse',
        'tab_builds',
        'tab_about',
        'main_window',
        'icon_provider',
        'data_loader',
        'engine',
        'skill_tree_widget',
        'perk_zh',
        # 显式声明 PySide6 核心模块，确保 PyInstaller 正确收集
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # === 大型模块（确定未使用，排除以减小体积）===
        'matplotlib', 'numpy', 'scipy', 'pandas',
        'tkinter',
        # === PySide6 大型子模块（确定未使用）===
        'PySide6.QtWebEngine',      # 嵌入式浏览器，极大
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtQuick',          # QML 引擎
        'PySide6.QtQuick3D',
        'PySide6.QtQml',
        'PySide6.QtQmlModels',
        'PySide6.Qt3D',             # 3D 渲染
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DExtras',
        'PySide6.QtDataVisualization',
        'PySide6.QtCharts',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtDesigner',       # UI 设计器
        'PySide6.QtHelp',
        'PySide6.QtPrintSupport',
        # === 开发/测试工具 ===
        'unittest', 'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BBR_SkillSimulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',
)

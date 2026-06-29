# -*- coding: utf-8 -*-
"""
main_window.py
主窗口：左侧导航 + 右侧 StackedWidget 承载四个页面。

页面：
  - 正向模拟 (tab_forward.ForwardTab)
  - 反向推导 (tab_reverse.ReverseTab)
  - 流派推荐 (tab_builds.BuildsTab)
  - 关于     (tab_about.AboutTab)

数据加载失败时显示错误页，禁用功能。
"""

import os
import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QStackedWidget, QLabel, QPushButton, QMessageBox, QStatusBar, QApplication,
)

from data_loader import load_data, DataError
from engine import SkillEngine
from icon_provider import IconProvider


class MainWindow(QMainWindow):
    """应用主窗口。"""

    NAV_ITEMS = [
        ("forward", "正向模拟", "选择背景与特性，查看技能树组出现概率分布"),
        ("reverse", "反向推导", "选择目标技能树组，找出最佳背景与特性组合"),
        ("builds", "流派推荐", "查看各背景的推荐加点方案与玩法建议"),
        ("about", "关于", "软件说明与数据版本"),
    ]

    def __init__(self, data_path=None):
        super().__init__()
        self.setWindowTitle("战场兄弟·重铸 — 技能树模拟器")
        self.resize(1180, 760)

        # 数据路径：exe 同目录 data.json
        if data_path is None:
            here = self._app_dir()
            data_path = os.path.join(here, "data.json")
        self.data_path = data_path

        # 加载数据
        self.gd = None
        self.engine = None
        self.icon_provider = None
        self._load_data_or_show_error()

        # 构建 UI
        self._build_ui()

        # 状态栏
        self._build_statusbar()

        if self.gd is not None:
            self._post_load_init()

    # ------------------------------------------------------------------
    # 路径与数据加载
    # ------------------------------------------------------------------

    def _app_dir(self):
        """返回程序所在目录（支持 PyInstaller 打包后）。"""
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def _load_data_or_show_error(self):
        """加载 data.json，失败时设 gd=None（UI 会显示错误页）。"""
        try:
            self.gd = load_data(self.data_path)
        except DataError as e:
            self.gd = None
            self._data_error = e
            # 不立即弹窗，等 UI 构建后显示错误页
            return
        except Exception as e:
            self.gd = None
            self._data_error = DataError(f"加载数据时发生未知错误：{e}", code="unknown")

    def _post_load_init(self):
        """数据加载成功后的初始化：引擎、图标、页面数据。"""
        self.engine = SkillEngine(self.gd)
        self.icon_provider = IconProvider(icons_dir=os.path.join(self._app_dir(), "icons"))
        # 通知各页面加载数据
        for page in [getattr(self, "forward_tab", None),
                     getattr(self, "reverse_tab", None),
                     getattr(self, "builds_tab", None)]:
            if page and hasattr(page, "on_data_ready"):
                try:
                    page.on_data_ready(self.gd, self.engine, self.icon_provider)
                except Exception as e:
                    self._show_error_msg("页面初始化失败", str(e))

    # ------------------------------------------------------------------
    # UI 构建
    # ------------------------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧导航
        self.nav = QListWidget()
        self.nav.setFixedWidth(200)
        self.nav.setIconSize(QSize(32, 32))
        for key, title, desc in self.NAV_ITEMS:
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, key)
            item.setToolTip(desc)
            self.nav.addItem(item)
        self.nav.setCurrentRow(0)
        self.nav.currentRowChanged.connect(self._on_nav_changed)
        layout.addWidget(self.nav)

        # 右侧内容区
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        if self.gd is None:
            # 数据加载失败 → 错误页
            self.stack.addWidget(self._build_error_page())
        else:
            # 四页面
            from tab_forward import ForwardTab
            from tab_reverse import ReverseTab
            from tab_builds import BuildsTab
            from tab_about import AboutTab
            self.forward_tab = ForwardTab()
            self.reverse_tab = ReverseTab()
            self.builds_tab = BuildsTab()
            self.about_tab = AboutTab()
            self.about_tab.set_info(self.gd)
            self.stack.addWidget(self.forward_tab)
            self.stack.addWidget(self.reverse_tab)
            self.stack.addWidget(self.builds_tab)
            self.stack.addWidget(self.about_tab)

    def _build_error_page(self):
        """数据加载失败时的错误页。"""
        page = QWidget()
        v = QVBoxLayout(page)
        v.setAlignment(Qt.AlignCenter)
        err = getattr(self, "_data_error", None)
        title = QLabel("⚠ 数据加载失败")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #c0392b;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)
        msg = QLabel(str(err) if err else "未知错误")
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 14px; padding: 20px;")
        msg.setAlignment(Qt.AlignCenter)
        msg.setMaximumWidth(700)
        v.addWidget(msg)

        hint = QLabel("请将 data.json 放置在程序同目录后重启本程序。")
        hint.setStyleSheet("font-size: 13px; color: #555; padding: 10px;")
        hint.setAlignment(Qt.AlignCenter)
        v.addWidget(hint)

        reload_btn = QPushButton("重新加载")
        reload_btn.clicked.connect(self._reload_data)
        v.addWidget(reload_btn, 0, Qt.AlignCenter)
        return page

    def _build_statusbar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        if self.gd is not None:
            sb.showMessage(f"数据版本: {self.gd.version}  |  背景 {len(self.gd.backgrounds)}  "
                           f"特性 {len(self.gd.traits)}  组 {len(self.gd.groups)}", 0)
        else:
            sb.showMessage("数据未加载", 0)

    # ------------------------------------------------------------------
    # 交互
    # ------------------------------------------------------------------

    def _on_nav_changed(self, row):
        if self.gd is None:
            return
        self.stack.setCurrentIndex(row)

    def _reload_data(self):
        """重新加载 data.json（错误页按钮）。"""
        try:
            self.gd = load_data(self.data_path)
            QMessageBox.information(self, "成功", "数据加载成功，请重启程序以加载界面。")
        except DataError as e:
            QMessageBox.critical(self, "加载失败", str(e))

    def _show_error_msg(self, title, text):
        QMessageBox.critical(self, title, text)

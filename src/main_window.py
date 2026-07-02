# -*- coding: utf-8 -*-
"""main_window.py - left nav + right stacked pages + language/theme toggle."""

import os
import sys
import traceback

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

import theme
from data_loader import _load_settings, _save_settings, load_data
from engine import SkillEngine
from i18n import set_lang as i18n_set_lang
from i18n import t
from icon_provider import IconProvider

NAV_ICONS = ["▶", "◀", "☰", "ⓘ"]
NAV_KEYS = ["nav.forward", "nav.reverse", "nav.builds", "nav.about"]


def _read_version():
    """Read version from VERSION file (one line). Falls back to 'dev'."""
    # Primary: VERSION next to exe (frozen) or in src/ (dev with VERSION copied)
    version_file = os.path.join(exe_dir(), "VERSION")
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        pass
    # Fallback: project root (dev mode where VERSION is ../ relative to src)
    try:
        version_file = os.path.join(os.path.dirname(exe_dir()), "VERSION")
        with open(version_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "dev"


def exe_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _user_qss_override():
    """exe 同级 style.qss 作为用户自定义覆盖层(可选)。"""
    qss_path = os.path.join(exe_dir(), "style.qss")
    if os.path.isfile(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return ""


def apply_app_theme():
    """按当前 theme 状态重建并应用全局 QSS。"""
    app = QApplication.instance()
    if app is not None:
        app.setStyleSheet(theme.build_qss() + "\n" + _user_qss_override())


class MainWindow(QMainWindow):

    def __init__(self, data_path=None):
        super().__init__()
        self._version = _read_version()
        self.setWindowTitle(f"BBR Skill Simulator v{self._version}")
        self.resize(1180, 760)
        self.setMinimumSize(960, 640)
        self.init_errors = []
        self._data_error = None

        if data_path is None:
            data_path = os.path.join(exe_dir(), "data.json")
        self.data_path = data_path

        # lang
        s = _load_settings(exe_dir())
        self.lang = s.get("lang", "zh")
        i18n_set_lang(self.lang)

        # load data
        self.gd = None
        self.engine = None
        self.icon_provider = None
        try:
            self.gd = load_data(self.data_path, lang=self.lang)
            if self.gd is None:
                raise Exception("load_data returned None")
            self.engine = SkillEngine(self.gd)
            self.icon_provider = IconProvider(icons_dir=os.path.join(exe_dir(), "icons"))
        except Exception as e:
            self._data_error = str(e) + "\n" + traceback.format_exc()
            self.gd = None

        # build UI
        self._build_ui()
        if self.gd is not None:
            self._build_statusbar()
            self._restore_state()

    def _restore_state(self):
        """Restore window geometry and last session state from settings."""
        s = _load_settings(exe_dir())
        win = s.get("window")
        if win and isinstance(win, dict):
            x = win.get("x")
            y = win.get("y")
            w = win.get("w")
            h = win.get("h")
            if all(v is not None for v in (x, y, w, h)):
                self.setGeometry(x, y, w, h)
        # Restore last tab
        last_tab = s.get("last_tab")
        if isinstance(last_tab, int) and 0 <= last_tab < self.nav.count():
            self.nav.setCurrentRow(last_tab)

    def closeEvent(self, event):
        """Save session state before closing."""
        s = _load_settings(exe_dir())
        # Window geometry
        g = self.geometry()
        s["window"] = {"x": g.x(), "y": g.y(), "w": g.width(), "h": g.height()}
        # Last active tab
        s["last_tab"] = self.nav.currentRow()
        _save_settings(exe_dir(), s)
        super().closeEvent(event)

    # ── language toggle ───────────────────────────────────────────

    def _toggle_lang(self):
        if self.gd is None:
            return
        nl = "en" if self.lang == "zh" else "zh"
        self.lang = nl
        i18n_set_lang(nl)
        try:
            # 读取-合并-写回，避免整体覆写丢失 window/last_tab 等其他键
            s = _load_settings(exe_dir())
            s["lang"] = nl
            _save_settings(exe_dir(), s)
        except Exception:
            pass
        self.gd.set_lang(nl)
        self._update_nav_labels()
        self._update_foot_buttons()
        # retranslate + data refresh for all tabs
        for pg in self._tabs():
            if hasattr(pg, "retranslate"):
                try:
                    pg.retranslate()
                except Exception:
                    pass
        for pg in self._tabs(include_about=False):
            if hasattr(pg, "on_data_ready"):
                try:
                    pg.on_data_ready(self.gd, self.engine, self.icon_provider)
                except Exception:
                    pass
        self._build_statusbar()

    # ── theme toggle ──────────────────────────────────────────────

    def _toggle_theme(self):
        new_name = "light" if theme.is_dark() else "dark"
        theme.set_theme(new_name)
        try:
            s = _load_settings(exe_dir())
            s["theme"] = new_name
            _save_settings(exe_dir(), s)
        except Exception:
            pass
        apply_app_theme()
        self._update_foot_buttons()
        # 让各页重刷代码里设置的颜色(表格文字色、技能树矩阵等)
        for pg in self._tabs():
            if hasattr(pg, "retheme"):
                try:
                    pg.retheme()
                except Exception:
                    pass

    def _tabs(self, include_about=True):
        names = ["forward_tab", "reverse_tab", "builds_tab"]
        if include_about:
            names.append("about_tab")
        return [getattr(self, n) for n in names if getattr(self, n, None) is not None]

    def _update_nav_labels(self):
        for i in range(min(len(NAV_KEYS), self.nav.count())):
            self.nav.item(i).setText(f"{NAV_ICONS[i]}  {t(NAV_KEYS[i])}")
        self.nav_title.setText(t("nav.title"))

    def _update_foot_buttons(self):
        """刷新导航底部语言/主题按钮的文字与提示。"""
        # 语言按钮显示目标语言
        self.lang_btn.setText("English" if self.lang == "zh" else "中文")
        self.lang_btn.setToolTip("切换到 English" if self.lang == "zh" else "Switch to 中文")
        # 主题按钮显示目标主题
        if theme.is_dark():
            self.theme_btn.setText("☀ " + t("theme.to_light"))
            self.theme_btn.setToolTip(t("theme.tip_light"))
        else:
            self.theme_btn.setText("🌙 " + t("theme.to_dark"))
            self.theme_btn.setToolTip(t("theme.tip_dark"))

    # ── UI construction ───────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---- nav panel ----
        nav_panel = QWidget()
        nav_panel.setObjectName("nav_panel")
        nav_panel.setFixedWidth(200)
        nl = QVBoxLayout(nav_panel)
        nl.setContentsMargins(0, 0, 0, 0)
        nl.setSpacing(0)
        nl.addSpacing(10)

        self.nav_title = QLabel(t("nav.title"))
        self.nav_title.setObjectName("nav_title")
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        self.nav_title.setFont(f)
        nl.addWidget(self.nav_title)
        nl.addSpacing(12)

        self.nav = QListWidget()
        self.nav.setObjectName("nav_list")
        for i, key in enumerate(NAV_KEYS):
            item = QListWidgetItem(f"{NAV_ICONS[i]}  {t(key)}")
            item.setData(Qt.UserRole, key)
            self.nav.addItem(item)
        self.nav.setCurrentRow(0)
        self.nav.currentRowChanged.connect(self._on_nav)
        nl.addWidget(self.nav, 1)

        # bottom: theme + lang toggles, then version
        nl.addSpacing(6)
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("nav_foot_btn")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._toggle_theme)
        nl.addWidget(self.theme_btn)

        self.lang_btn = QPushButton()
        self.lang_btn.setObjectName("nav_foot_btn")
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.clicked.connect(self._toggle_lang)
        nl.addWidget(self.lang_btn)
        self._update_foot_buttons()

        nl.addSpacing(6)
        version_lbl = QLabel(f"v{self._version}")
        version_lbl.setObjectName("nav_version")
        nl.addWidget(version_lbl)

        layout.addWidget(nav_panel)

        # ---- content ----
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        if self.gd is None:
            self.stack.addWidget(self._error_page())
        else:
            self._build_tabs()

    def _build_tabs(self):
        try:
            from tab_about import AboutTab
            from tab_builds import BuildsTab
            from tab_forward import ForwardTab
            from tab_reverse import ReverseTab
            self.forward_tab = ForwardTab()
            self.reverse_tab = ReverseTab()
            self.builds_tab = BuildsTab()
            self.about_tab = AboutTab()
            self.about_tab.set_info(self.gd)
            self.stack.addWidget(self.forward_tab)
            self.stack.addWidget(self.reverse_tab)
            self.stack.addWidget(self.builds_tab)
            self.stack.addWidget(self.about_tab)
            for pg in [self.forward_tab, self.reverse_tab, self.builds_tab]:
                if pg and hasattr(pg, "on_data_ready"):
                    pg.on_data_ready(self.gd, self.engine, self.icon_provider)
            self._setup_shortcuts()
        except Exception:
            self.gd = None
            self._data_error = "[tabs] " + traceback.format_exc()
            self.stack.addWidget(self._error_page())

    def _error_page(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignCenter)
        tt = QLabel("DATA LOAD FAILED")
        tt.setStyleSheet(f"font-size:22px;font-weight:bold;color:{theme.c('error_border')};")
        tt.setAlignment(Qt.AlignCenter)
        lay.addWidget(tt)
        detail = self._data_error or "(no details)"
        m = QLabel(detail + "\n\npath: " + str(self.data_path))
        m.setWordWrap(True)
        m.setStyleSheet("font-size:13px;padding:20px;font-family:Consolas,monospace;")
        m.setAlignment(Qt.AlignCenter)
        m.setMaximumWidth(750)
        lay.addWidget(m)
        hint = QLabel("Put data.json next to the exe and restart.")
        hint.setStyleSheet(f"font-size:13px;color:{theme.c('text_muted')};padding:10px;")
        hint.setAlignment(Qt.AlignCenter)
        lay.addWidget(hint)
        b = QPushButton("Retry")
        b.clicked.connect(self._retry)
        lay.addWidget(b, 0, Qt.AlignCenter)
        return w

    def _retry(self):
        try:
            self.gd = load_data(self.data_path, lang=self.lang)
            if self.gd is None:
                raise Exception("load_data returned None")
            self.engine = SkillEngine(self.gd)
            self.icon_provider = IconProvider(icons_dir=os.path.join(exe_dir(), "icons"))
            self._data_error = None
        except Exception as e:
            QMessageBox.critical(self, "Failed", str(e))
            return
        # rebuild
        central = self.centralWidget()
        if central:
            central.deleteLater()
        self._build_ui()
        self._build_statusbar()

    def _build_statusbar(self):
        """状态栏:右侧常驻数据版本,左侧留给临时反馈消息(如「已复制」)。"""
        sb = QStatusBar()
        self.setStatusBar(sb)
        if self.gd is not None:
            info = QLabel(t("status.data_version") + str(getattr(self.gd, "version", "?")))
            sb.addPermanentWidget(info)

    def _on_nav(self, row):
        self.stack.setCurrentIndex(row)

    def _setup_shortcuts(self):
        for i in range(1, 5):
            sc = QShortcut(QKeySequence("Ctrl+" + str(i)), self)
            sc.activated.connect(lambda idx=i-1: self._on_nav(idx))

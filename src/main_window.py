# -*- coding: utf-8 -*-
"""main_window.py - left nav + right stacked pages + language/theme toggle."""

import os
import traceback

from PySide6.QtCore import QSize, Qt
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
from app_paths import external_app_dir, resolve_resource
from data_loader import _load_settings, _save_settings, load_data
from engine import SkillEngine
from i18n import set_lang as i18n_set_lang
from i18n import t
from icon_provider import IconProvider

NAV_ICON_KEYS = ["forward", "reverse", "builds", "about"]
NAV_KEYS = ["nav.forward", "nav.reverse", "nav.builds", "nav.about"]


def _read_version():
    """Read version from VERSION file (one line). Falls back to 'dev'."""
    try:
        version_file = resolve_resource("VERSION", include_project_root=True)
        with open(version_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "dev"


def exe_dir():
    return external_app_dir()


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
            data_path = resolve_resource("data.json")
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
        # 先停掉仍在运行的反向推导后台线程，避免「线程仍在运行时被销毁」崩溃
        rev = getattr(self, "reverse_tab", None)
        worker = getattr(rev, "_worker", None) if rev else None
        if worker is not None and worker.isRunning():
            worker.requestInterruption()
            if not worker.wait(5000):
                event.ignore()
                return
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
            self.nav.item(i).setText(t(NAV_KEYS[i]))
        self.nav_title.setText(t("nav.title"))

    def _update_foot_buttons(self):
        """刷新导航底部语言/主题按钮的文字与提示,并设置图标。"""
        ip = getattr(self, "icon_provider", None)
        nav_color = theme.c("nav_text_faint")
        # 语言按钮
        self.lang_btn.setText(" English" if self.lang == "zh" else " 中文")
        self.lang_btn.setToolTip("切换到 English" if self.lang == "zh" else "Switch to 中文")
        if ip is not None:
            self.lang_btn.setIcon(ip.get_lang_icon(nav_color, 16))
        # 主题按钮
        if theme.is_dark():
            self.theme_btn.setText(" " + t("theme.to_light"))
            self.theme_btn.setToolTip(t("theme.tip_light"))
            if ip is not None:
                self.theme_btn.setIcon(ip.get_theme_icon(True, nav_color, 16))
        else:
            self.theme_btn.setText(" " + t("theme.to_dark"))
            self.theme_btn.setToolTip(t("theme.tip_dark"))
            if ip is not None:
                self.theme_btn.setIcon(ip.get_theme_icon(False, nav_color, 16))

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
        self.nav.setIconSize(QSize(22, 22))
        self.nav.setSpacing(1)
        for i, key in enumerate(NAV_KEYS):
            item = QListWidgetItem(t(key))
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
        self.theme_btn.setIconSize(QSize(16, 16))
        self.theme_btn.clicked.connect(self._toggle_theme)
        nl.addWidget(self.theme_btn)

        self.lang_btn = QPushButton()
        self.lang_btn.setObjectName("nav_foot_btn")
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.setIconSize(QSize(16, 16))
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
            self.reverse_tab.open_in_forward.connect(self._open_in_forward)
            self._setup_shortcuts()
        except Exception:
            self.gd = None
            self._data_error = "[tabs] " + traceback.format_exc()
            self.stack.addWidget(self._error_page())

    def _error_page(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignCenter)
        tt = QLabel(t("error.data_load_title"))
        tt.setObjectName("error_page_title")
        tt.setAlignment(Qt.AlignCenter)
        lay.addWidget(tt)
        detail = self._data_error or t("error.data_load_no_details")
        m = QLabel(detail + "\n\n" + t("error.data_load_path").format(self.data_path))
        m.setWordWrap(True)
        m.setObjectName("error_page_detail")
        m.setAlignment(Qt.AlignCenter)
        m.setMaximumWidth(750)
        lay.addWidget(m)
        hint = QLabel(t("error.data_load_hint"))
        hint.setObjectName("error_page_hint")
        hint.setAlignment(Qt.AlignCenter)
        lay.addWidget(hint)
        b = QPushButton(t("error.retry"))
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
            QMessageBox.critical(self, t("error.retry_failed"), str(e))
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

    def _open_in_forward(self, bg_id, trait_ids):
        """逆向页结果 → 正向页:填入组合、计算并切页。"""
        if self.forward_tab.load_config(bg_id, trait_ids):
            self.nav.setCurrentRow(0)
        else:
            self.statusBar().showMessage(t("reverse.bg_hidden"), 3000)

    def _setup_shortcuts(self):
        for i in range(1, 5):
            sc = QShortcut(QKeySequence("Ctrl+" + str(i)), self)
            # 走 nav 切页,左侧导航高亮随之同步
            sc.activated.connect(lambda idx=i-1: self.nav.setCurrentRow(idx))

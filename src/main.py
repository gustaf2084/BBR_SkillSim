# -*- coding: utf-8 -*-
"""
main.py
Entry point. Launches main window, handles global exceptions.

The single-file exe needs data.json and (optionally) an icons folder next to it.
"""

import os
import sys
import traceback

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

import theme
from i18n import t


def get_app_dir():
    """Return the directory containing the executable (supports PyInstaller frozen)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def locate_data_json():
    """Find data.json: prefer exe-adjacent copy (user-updatable), else bundled fallback."""
    external = os.path.join(get_app_dir(), "data.json")
    if os.path.isfile(external):
        return external
    # PyInstaller onefile mode: resources are in _MEIPASS temp directory
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundled = os.path.join(sys._MEIPASS, "data.json")
        if os.path.isfile(bundled):
            return bundled
    # Fallback: still return the adjacent path so loading logic gives a clear error
    return external


def load_user_qss_override():
    """exe 同级的 style.qss 为用户自定义覆盖层,追加在生成的主题 QSS 之后。"""
    qss_path = os.path.join(get_app_dir(), "style.qss")
    if os.path.isfile(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return ""


def main():
    # High DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("BBR Skill Simulator")

    # Theme: read saved preference before building any UI
    from data_loader import _load_settings
    settings = _load_settings(get_app_dir())
    theme.set_theme(settings.get("theme", "light"))
    app.setStyleSheet(theme.build_qss() + "\n" + load_user_qss_override())

    # Global exception hook: show dialog instead of crashing silently
    def global_excepthook(exc_type, exc_value, exc_tb):
        tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        try:
            QMessageBox.critical(
                None, t("error.global_title"),
                t("error.global_body").format(str(exc_value), tb_text[:800]))
        except Exception:
            sys.__excepthook__(exc_type, exc_value, exc_tb)
    sys.excepthook = global_excepthook

    # Lazy import to avoid blocking error page on data load failure
    from main_window import MainWindow
    data_path = locate_data_json()
    win = MainWindow(data_path=data_path)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

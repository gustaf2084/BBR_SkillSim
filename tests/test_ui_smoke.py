# -*- coding: utf-8 -*-
"""关键 Qt 界面的离屏冒烟测试。"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from i18n import set_lang, t
from main_window import MainWindow
from tab_reverse import ReverseDeriveWorker


def _app():
    return QApplication.instance() or QApplication([])


def test_main_window_forward_flow_and_reverse_mode():
    app = _app()
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "data.json"))
    win = MainWindow(data_path=data_path)

    assert win.gd is not None
    assert win.stack.count() == 4
    assert win.forward_tab.bg_combo.count() == 92

    win.forward_tab._on_calculate()
    assert win.forward_tab.result_table.rowCount() == 48

    assert not hasattr(win.reverse_tab, "mode_combo")

    win.deleteLater()
    app.processEvents()


def test_reverse_worker_keeps_native_finished_signal():
    assert hasattr(ReverseDeriveWorker, "result_ready")


def test_finished_old_worker_does_not_clear_new_worker():
    app = _app()
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "data.json"))
    win = MainWindow(data_path=data_path)

    class FinishedWorker:
        deleted = False

        def deleteLater(self):
            self.deleted = True

    old_worker = FinishedWorker()
    new_worker = object()
    win.reverse_tab._worker = new_worker

    win.reverse_tab._on_worker_thread_finished(old_worker)

    assert old_worker.deleted is True
    assert win.reverse_tab._worker is new_worker
    win.reverse_tab._worker = None
    win.deleteLater()
    app.processEvents()


def test_close_is_ignored_if_reverse_worker_does_not_stop():
    app = _app()
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "data.json"))
    win = MainWindow(data_path=data_path)

    class StuckWorker:
        interrupted = False

        def isRunning(self):
            return True

        def requestInterruption(self):
            self.interrupted = True

        def wait(self, _timeout):
            return False

    class CloseEvent:
        ignored = False

        def ignore(self):
            self.ignored = True

    worker = StuckWorker()
    event = CloseEvent()
    win.reverse_tab._worker = worker

    win.closeEvent(event)

    assert worker.interrupted is True
    assert event.ignored is True
    win.reverse_tab._worker = None
    win.deleteLater()
    app.processEvents()


def test_data_load_error_strings_are_translated():
    try:
        set_lang("zh")
        assert t("error.data_load_title") == "数据加载失败"
        assert t("error.retry") == "重试"
        set_lang("en")
        assert t("error.data_load_title") == "Data Load Failed"
        assert t("error.retry") == "Retry"
    finally:
        set_lang("zh")


def test_analytic_mode_label_describes_exact_calculation():
    try:
        set_lang("zh")
        assert t("mode.analytic") == "精确解析"
        assert t("mode.monte") == "蒙特卡洛抽样"
        set_lang("en")
        assert t("mode.analytic") == "Exact analytic"
        assert t("mode.monte") == "Monte Carlo sampling"
    finally:
        set_lang("zh")

# -*- coding: utf-8 -*-
"""UI 体验优化的离屏冒烟测试:实时计算、逆向→正向联动、目标标签栏、排序、快捷键。"""

import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from main_window import MainWindow
from ui_components import SORT_ROLE

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "data.json"))


def _app():
    return QApplication.instance() or QApplication([])


def _pump(app, ms=400):
    """处理事件直到防抖定时器有机会触发。"""
    end = time.monotonic() + ms / 1000
    while time.monotonic() < end:
        app.processEvents()


@pytest.fixture
def win():
    app = _app()
    w = MainWindow(data_path=DATA_PATH)
    _pump(app)
    yield w
    w.deleteLater()
    app.processEvents()


def test_forward_live_recalc_in_analytic_mode(win):
    app = _app()
    ft = win.forward_tab
    # 启动后自动出结果
    assert ft.result_table.rowCount() > 0
    before = dict(ft._last_results)

    ft._trait_checkboxes[0].setChecked(True)
    ft._trait_checkboxes[1].setChecked(True)
    assert ft._recalc_timer.isActive()  # 防抖中,尚未计算
    _pump(app)
    assert dict(ft._last_results) != before


def test_forward_monte_carlo_does_not_auto_recalc(win):
    app = _app()
    ft = win.forward_tab
    ft.mode_combo.setCurrentIndex(ft.mode_combo.findData("monte_carlo"))
    _pump(app)
    snapshot = ft._last_results
    ft._trait_checkboxes[0].setChecked(True)
    assert not ft._recalc_timer.isActive()
    _pump(app)
    assert ft._last_results is snapshot


def test_reverse_open_in_forward_fills_config_and_switches_page(win):
    traits = sorted(win.gd.traits)[:2]
    win.nav.setCurrentRow(1)
    win.reverse_tab.open_in_forward.emit("caravan_hand_southern_background", traits)

    ft = win.forward_tab
    assert win.nav.currentRow() == 0
    assert win.stack.currentIndex() == 0
    # 重复背景映射到列表代表项
    assert ft.bg_combo.currentData() == "caravan_hand_background"
    assert sorted(cb.property("trait_id") for cb in ft._selected_traits()) == traits
    assert ft.result_table.rowCount() > 0


def test_reverse_open_hidden_background_shows_status(win):
    bg_before = win.forward_tab.bg_combo.currentData()
    win.reverse_tab.open_in_forward.emit("companion_1h_background", [])
    assert win.forward_tab.bg_combo.currentData() == bg_before
    assert win.statusBar().currentMessage()


def test_reverse_target_chips_sync_with_checkboxes(win):
    rt = win.reverse_tab
    assert rt.target_chips.isHidden()
    boxes = list(rt._iter_checkboxes())
    for idx in (0, 3, 7):
        boxes[idx][0].setChecked(True)
    assert rt.target_chips.keys() == rt._checked_targets()
    assert not rt.target_chips.isHidden()

    rt.target_chips.removed.emit(boxes[3][1])
    assert not boxes[3][0].isChecked()
    assert boxes[3][1] not in rt.target_chips.keys()

    rt.target_chips.cleared.emit()
    assert rt._checked_targets() == []
    assert rt.target_chips.isHidden()


def test_result_tables_sort_numerically(win):
    ft = win.forward_tab
    table = ft.result_table
    table.sortItems(3, Qt.AscendingOrder)
    values = [table.item(r, 3).data(SORT_ROLE) for r in range(table.rowCount())]
    assert values == sorted(values)
    # 重新填表后仍按当前指示排序,且行内数据一致
    ft._fill_table(ft._last_results)
    for r in range(table.rowCount()):
        gid = table.item(r, 1).data(Qt.UserRole)
        assert table.item(r, 4).data(Qt.UserRole) == pytest.approx(ft._last_results[gid])

    rt = win.reverse_tab
    rows = [
        ("farmhand_background", (), 0.2, {"Dagger": 0.2}, 1.5),
        ("thief_background", (), 0.9, {"Dagger": 0.9}, 0.4),
        ("hunter_background", (), 0.55, {"Dagger": 0.55}, 3.0),
    ]
    rt._fill_table(rows, False)
    rt.result_table.sortItems(2, Qt.DescendingOrder)
    scores = [rt.result_table.item(r, 2).data(SORT_ROLE) for r in range(3)]
    assert scores == [0.9, 0.55, 0.2]
    # 平均概率条与得分同行
    for r in range(3):
        assert rt.result_table.item(r, 3).data(Qt.UserRole) == pytest.approx(scores[r])


def test_ctrl_f_focuses_current_page_search(win):
    app = _app()
    win.show()
    for row, attr in ((0, "trait_search"), (1, "target_search"), (2, "bg_search")):
        win.nav.setCurrentRow(row)
        win._focus_current_search()
        app.processEvents()
        page = win.stack.currentWidget()
        assert QApplication.focusWidget() is getattr(page, attr)

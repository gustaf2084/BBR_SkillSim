# -*- coding: utf-8 -*-
"""
ui_components.py
统一的可复用 UI 组件：空状态、错误状态、引导提示。
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


def make_placeholder(text, sub_text=""):
    """创建就绪/等待状态提示组件。"""
    w = QWidget()
    v = QVBoxLayout(w)
    v.setAlignment(Qt.AlignCenter)
    v.setContentsMargins(20, 40, 20, 40)

    icon = QLabel("◈")
    icon.setStyleSheet("font-size: 28px; color: #C8BFA8;")
    icon.setAlignment(Qt.AlignCenter)
    v.addWidget(icon)

    label = QLabel(text)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("font-size: 15px; color: #6B6359; padding: 10px;")
    v.addWidget(label)

    if sub_text:
        sub = QLabel(sub_text)
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("font-size: 12px; color: #A09888;")
        v.addWidget(sub)

    return w


def make_notice_parchment(title, body):
    """创建羊皮纸便签风格提示（无结果/空状态）。"""
    w = QWidget()
    w.setObjectName("notice_parchment")
    v = QVBoxLayout(w)

    t = QLabel(title)
    t.setObjectName("notice_parchment_title")
    t.setWordWrap(True)
    v.addWidget(t)

    b = QLabel(body)
    b.setWordWrap(True)
    b.setStyleSheet("font-size: 14px; color: #1C1814; padding-top: 4px;")
    v.addWidget(b)

    return w


def make_error_notice(title, body):
    """创建错误提示组件。"""
    w = QWidget()
    w.setObjectName("notice_error")
    v = QVBoxLayout(w)

    t = QLabel(title)
    t.setStyleSheet("font-size: 16px; font-weight: bold; color: #8B1A1A;")
    t.setWordWrap(True)
    v.addWidget(t)

    b = QLabel(body)
    b.setWordWrap(True)
    b.setStyleSheet("font-size: 13px; color: #5A1A1A; padding-top: 4px;")
    v.addWidget(b)

    return w

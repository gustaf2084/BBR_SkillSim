# -*- coding: utf-8 -*-
"""
main.py
程序入口。启动主窗口，处理全局异常。

打包后单文件 exe 同目录需有 data.json 与（可选）icons 文件夹。
"""

import os
import sys
import traceback

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox


def get_app_dir():
    """返回程序所在目录（支持 PyInstaller frozen）。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def locate_data_json():
    """查找 data.json：优先 exe 同级目录（便于用户更新），否则使用打包内置副本。"""
    external = os.path.join(get_app_dir(), "data.json")
    if os.path.isfile(external):
        return external
    # PyInstaller onefile 模式下资源在 _MEIPASS 临时目录
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundled = os.path.join(sys._MEIPASS, "data.json")
        if os.path.isfile(bundled):
            return bundled
    # 兜底：仍返回同级目录路径，让后续加载逻辑报清晰错误
    return external


def main():
    # 高 DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("BBR Skill Simulator")

    # 全局异常 hook：未捕获异常弹窗而非崩溃
    def global_excepthook(exc_type, exc_value, exc_tb):
        tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        # 尝试弹窗
        try:
            QMessageBox.critical(
                None, "发生错误",
                f"程序遇到未处理的错误：\n\n{exc_value}\n\n详细信息已记录。\n\n{tb_text[:800]}")
        except Exception:
            sys.__excepthook__(exc_type, exc_value, exc_tb)
    sys.excepthook = global_excepthook

    # 延迟导入，避免数据加载失败时影响错误页
    from main_window import MainWindow
    data_path = locate_data_json()
    win = MainWindow(data_path=data_path)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

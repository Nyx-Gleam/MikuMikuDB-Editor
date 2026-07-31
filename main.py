"""
main.py
=======
Entry point for the application.
"""
from __future__ import annotations

import os
import sys
import threading

from core.crash_logger import install_crash_logging, install_qt_exception_hook


def _apply_windows_qt_multimedia_workaround():
    """
    Adds the PySide6 installation directory to the Windows DLL search path
    before creating the QApplication.

    This helps Qt locate the QtMultimedia backend on systems where it is
    not found automatically. No action is taken on non-Windows platforms.
    """
    if sys.platform != "win32":
        return
    try:
        import sysconfig
        pyside6_dir = os.path.join(sysconfig.get_path("purelib"), "PySide6")
        if os.path.isdir(pyside6_dir) and hasattr(os, "add_dll_directory"):
            os.add_dll_directory(pyside6_dir)
    except Exception:
        pass  # Best-effort. If this fails, continue and let Qt handle the error normally.


def main():
    install_crash_logging()
    _apply_windows_qt_multimedia_workaround()

    from PySide6.QtWidgets import QApplication
    from ui.theme import DARK_QSS
    from ui.main_window import MainWindow
    from core import pv_ids_manager

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)

    install_qt_exception_hook()

    # Initialize the PV database in a background thread to avoid delaying
    # the first UI frame during application startup.
    threading.Thread(target=pv_ids_manager.initialize_pvdb, daemon=True).start()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


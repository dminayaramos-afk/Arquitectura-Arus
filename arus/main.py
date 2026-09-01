#!/usr/bin/env python3
"""
ARUS Launcher
"""

from __future__ import annotations

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import QApplication
from arus.interface.main_window import ARUSWindow


def main() -> int:
    app = QApplication(sys.argv)

    window = ARUSWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""conftest.py — make src/ importable for all tests; shared path constants."""

import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, SRC_DIR)

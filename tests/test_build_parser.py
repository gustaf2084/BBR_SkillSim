# -*- coding: utf-8 -*-
"""Unit tests for build_parser.py."""

import os
import sys
import tempfile

_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if _src not in sys.path:
    sys.path.insert(0, _src)

from build_parser import generate_template, parse_build_file


def test_blank_template_is_not_valid_build():
    with tempfile.TemporaryDirectory() as tmp:
        path = generate_template("assassin_background", "Assassin", tmp, lang="en")
        build = parse_build_file(path)
        assert build is not None
        assert build.is_valid() is False
        assert build.perks == []


def test_perk_name_may_contain_comma():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as f:
        f.write(
            "[build]\n"
            "name = Test\n"
            "background = assassin_background\n"
            "\n"
            "[perks]\n"
            "1 = Dagger, Tier 1, Perk, With Comma\n")
        path = f.name
    try:
        build = parse_build_file(path)
        assert build is not None
        assert build.is_valid() is True
        assert build.perks == [(1, "Dagger", "Tier 1", "Perk, With Comma")]
    finally:
        os.remove(path)

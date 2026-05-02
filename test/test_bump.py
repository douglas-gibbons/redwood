import unittest
from unittest.mock import patch, MagicMock

import pytest
import bump

def convert_semvers(input: list[str]) -> list[bump.SemVer]:

    svs: list[bump.SemVer] = []
    for i in input:
        sv = bump.make_semver(i)
        svs.append(sv)
    return svs


def test_highest_semver_basic():
    input = [
        "v0.0.0",
        "v1.0.0",
        "v01.00.01",
        "v1.1.0",
        "v2.0.0",
        "v2.0.1",
        "v02.01.0-alpha",
    ]
    sv = bump.highest_semver(convert_semvers(input))
    assert str(sv) == "v2.1.0"

def test_highest_semver_blank():
    input = []
    sv = bump.highest_semver(convert_semvers(input))
    assert str(sv) == "v0.0.0"

def test_highest_semver_strings():
    input = ["1.0.0-alpha1", "1.0.0-alpha2"]
    sv = bump.highest_semver(convert_semvers(input))
    assert str(sv) == "v1.0.0"

def test_highest_semver_v():
    input = ["v1.0.0-alpha1", "v2.0.1"]
    sv = bump.highest_semver(convert_semvers(input))
    assert str(sv) == "v2.0.1"



import pytest
from csv2anki import core
import os


def test_unpack():
    core.unpack("default.apkg", "default")
    assert os.path.isdir("default")

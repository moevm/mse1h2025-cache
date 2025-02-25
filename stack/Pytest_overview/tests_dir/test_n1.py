import pytest


def add(a: int, b: int) -> int:
    return a + b


def test_1():
    assert add(1, 1) == 2
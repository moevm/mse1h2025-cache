import pytest


def mult(a: int, b: int) -> int:
    return a * b


def test_1():
    assert mult(2, 3) == 6

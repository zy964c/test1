import pytest

from dataclasses import dataclass


@dataclass
class Row():
    id: int
    name: str


@pytest.fixture(autouse=True)
def result():
    return [Row(id=1, name='Test 1'),
            Row(id=2, name='Test 2')]

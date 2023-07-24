import pytest

from dataclasses import dataclass


@dataclass
class Row():
    id: int
    name: str


@pytest.fixture(autouse=True)
def result():
    return [Row(id=i, name=f'Test {i}') for i in range(1, 61)]

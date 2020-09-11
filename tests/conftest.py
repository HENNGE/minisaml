from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture
def read() -> Callable[[str], bytes]:
    def reader(filename: str) -> bytes:
        with Path(__file__).parent.joinpath("data", filename).open("rb") as fobj:
            return fobj.read()

    return reader

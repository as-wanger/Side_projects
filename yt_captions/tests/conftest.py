import pytest
import sys


@pytest.fixture
def capture_stdout(monkeypatch):
    buffer = {"stdout": "", "write_calls": 0}

    def fake_write(text):
        buffer["stdout"] += text
        buffer["write_calls"] += 1

    monkeypatch.setattr(sys.stdout, "write", fake_write)
    return buffer


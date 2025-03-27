import shutil
from pathlib import Path

import pytest
from citool.blueprint import detect_stack


@pytest.mark.parametrize(
    "fixture, expected",
    [
        ("python_setup", "python"),
        ("c_make", "c"),
        ("java_maven", "java"),
        ("unknown", "unknown"),
    ],
)
def test_detect_stack(fixture, expected, tmp_path: Path):
    base = Path(__file__).parent / "fixtures" / fixture
    for file in base.iterdir():
        shutil.copy(file, tmp_path / file.name)

    result = detect_stack(tmp_path) or {
        "language": "unknown",
        "build_system": "none",
        "build_commands": [],
    }
    assert result["language"] == expected

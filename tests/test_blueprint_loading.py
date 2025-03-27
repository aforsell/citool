import shutil
import yaml
import pytest
from pathlib import Path

from citool.blueprint import load_or_generate_blueprint
from citool.config import Config


def test_load_existing_blueprint(tmp_path: Path):
    blueprint_data = {
        "language": "python",
        "build_system": "setuptools",
        "build_commands": ["python setup.py install"],
        "ci": "gitlab",
        "env": "dev",
    }

    blueprint_path = tmp_path / "blueprint.yaml"
    with open(blueprint_path, "w") as f:
        yaml.dump(blueprint_data, f)

    config = Config(ci="gitlab", env="dev", dry_run=True)

    result = load_or_generate_blueprint(tmp_path, config)
    assert result["language"] == "python"
    assert result["build_system"] == "setuptools"
    assert result["ci"] == "gitlab"


def test_generate_blueprint_from_detection(tmp_path: Path):
    fixture = Path(__file__).parent / "fixtures" / "python_setup"
    for file in fixture.iterdir():
        shutil.copy(file, tmp_path / file.name)

    config = Config(ci="gitlab", env="dev", dry_run=True)

    result = load_or_generate_blueprint(tmp_path, config)
    assert result["language"] == "python"
    assert result["build_system"] == "setuptools"
    assert result["ci"] == "gitlab"
    assert result["env"] == "dev"


def test_unknown_stack_user_accepts(tmp_path: Path, monkeypatch):
    config = Config(ci="gitlab", env="dev", dry_run=False)

    # User says yes
    monkeypatch.setattr("citool.blueprint.ask", lambda msg: True)

    result = load_or_generate_blueprint(tmp_path, config)
    blueprint_file = tmp_path / "blueprint.yaml"

    assert result["language"] == "unknown"
    assert result["build_system"] == "none"
    assert blueprint_file.exists()


def test_abort_on_unknown_stack_and_user_declines(tmp_path: Path, monkeypatch):
    # No files -> unknown stack
    config = Config(ci="gitlab", env="dev", dry_run=True)

    # User says no
    monkeypatch.setattr("citool.blueprint.ask", lambda msg: False)

    with pytest.raises(SystemExit):
        load_or_generate_blueprint(tmp_path, config)


def test_detected_and_user_accepts_write(tmp_path: Path, monkeypatch):
    fixture = Path(__file__).parent / "fixtures" / "python_setup"
    for file in fixture.iterdir():
        shutil.copy(file, tmp_path / file.name)

    config = Config(ci="gitlab", env="dev", dry_run=False)

    # User says yes
    monkeypatch.setattr("citool.blueprint.ask", lambda msg: True)

    result = load_or_generate_blueprint(tmp_path, config)
    blueprint_file = tmp_path / "blueprint.yaml"

    assert result["language"] == "python"
    assert blueprint_file.exists()

    with open(blueprint_file) as f:
        written = yaml.safe_load(f)
        assert written["ci"] == "gitlab"
        assert written["env"] == "dev"


def test_detected_but_user_declines_write(tmp_path: Path, monkeypatch):
    fixture = Path(__file__).parent / "fixtures" / "python_setup"
    for file in fixture.iterdir():
        shutil.copy(file, tmp_path / file.name)

    config = Config(ci="gitlab", env="dev", dry_run=False)

    # User says no
    monkeypatch.setattr("citool.blueprint.ask", lambda msg: False)

    result = load_or_generate_blueprint(tmp_path, config)
    assert result["language"] == "python"
    assert not (tmp_path / "blueprint.yaml").exists()

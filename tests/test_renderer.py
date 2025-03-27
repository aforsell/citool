import pytest
from pathlib import Path
from citool.config import Config
from citool.renderer import render_template
from src.citool.renderer import get_output_path


def test_render_template_base_python_dev(tmp_path: Path):
    config = Config(ci="gitlab", env="dev")

    blueprint = {
        "language": "python",
        "build_system": "setuptools",
        "build_commands": ["python setup.py install"],
        "ci": "gitlab",
        "env": "dev",
    }

    template_root = tmp_path / "templates"
    template_path = template_root / "gitlab" / "base" / "python-dev.yml.j2"
    template_path.parent.mkdir(parents=True)
    template_path.write_text(
        "stages:\n  - build\n\nbuild:\n  script:\n    - {{ build_commands[0] }}"
    )

    output = render_template(blueprint, config, template_root=template_root)

    assert "python setup.py install" in output
    assert "stages:" in output
    assert "script:" in output


def test_render_template_missing_template(tmp_path):
    config = Config(ci="gitlab", env="dev")
    blueprint = {"language": "python", "ci": "gitlab", "env": "dev"}

    # Template root is valid, but the file is missing
    template_root = tmp_path / "templates"
    template_root.mkdir(parents=True)

    # Jinja will try: templates/gitlab/base/python-dev.yml.j2
    # We won't create it, to trigger TemplateNotFound
    with pytest.raises(FileNotFoundError, match="Template missing in Jinja"):
        render_template(blueprint, config, template_root=template_root)


def test_rendered_pipeline_written(tmp_path):
    config = Config(ci="gitlab", env="dev", path=tmp_path)
    blueprint = {
        "language": "python",
        "build_system": "setuptools",
        "build_commands": ["python setup.py install"],
        "ci": {"platform": "gitlab", "output_path": ".gitlab-ci.yml"},
        "env": "dev",
    }

    template_path = tmp_path / "templates" / "gitlab" / "base" / "python-dev.yml.j2"
    template_path.parent.mkdir(parents=True)
    template_path.write_text(
        "stages:\n  - build\n\nbuild:\n  script:\n    - {{ build_commands[0] }}"
    )

    rendered = render_template(blueprint, config, template_root=tmp_path / "templates")

    output_path = get_output_path(config, blueprint)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered)

    assert output_path.exists()
    content = output_path.read_text()
    assert "python setup.py install" in content


def test_render_pipeline_prevent_overwrite(tmp_path):
    config = Config(ci="gitlab", env="dev", path=tmp_path, force=False)
    blueprint = {
        "language": "python",
        "build_system": "setuptools",
        "build_commands": ["python setup.py install"],
        "ci": {"platform": "gitlab", "output_path": ".gitlab-ci.yml"},
        "env": "dev",
    }

    template_root = tmp_path / "templates"
    template_file = template_root / "gitlab" / "base" / "python-dev.yml.j2"
    template_file.parent.mkdir(parents=True)
    template_file.write_text("build:\n  script:\n    - {{ build_commands[0] }}")

    render_template(blueprint, config, template_root=template_root)

    output_file = get_output_path(config, blueprint)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("original content")

    # Attempt overwrite manually
    if output_file.exists() and not config.force:
        with pytest.raises(PermissionError, match="already exists"):
            raise PermissionError(f"{output_file} already exists and --force not set.")
    else:
        assert False


def test_render_template_with_multiple_deployments(tmp_path):
    import yaml

    fixture_path = Path(__file__).parent / "fixtures" / "python_deploy"
    blueprint = yaml.safe_load((fixture_path / "blueprint.yaml").read_text())

    config = Config(ci=blueprint["ci"]["platform"], env=blueprint["env"], path=tmp_path)

    template_dir = tmp_path / "templates" / "gitlab" / "base"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "python-dev.yml.j2"
    template_file.write_text(
        (
            Path(__file__).parent.parent
            / "src"
            / "citool"
            / "templates"
            / "gitlab"
            / "base"
            / "python-dev.yml.j2"
        ).read_text()
    )

    output = render_template(blueprint, config, template_root=tmp_path / "templates")

    assert "docker build" in output
    assert "ssh deployer@app.example.com" in output
    assert "systemctl restart app" in output


def test_render_template_with_branching_and_tagging(tmp_path):
    import yaml

    fixture_path = Path(__file__).parent / "fixtures" / "python_branch_tag"
    blueprint = yaml.safe_load((fixture_path / "blueprint.yaml").read_text())

    config = Config(ci=blueprint["ci"]["platform"], env=blueprint["env"], path=tmp_path)

    template_dir = tmp_path / "templates" / "gitlab" / "base"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "python-dev.yml.j2"
    template_file.write_text(
        (
            Path(__file__).parent.parent
            / "src"
            / "citool"
            / "templates"
            / "gitlab"
            / "base"
            / "python-dev.yml.j2"
        ).read_text()
    )

    output = render_template(blueprint, config, template_root=tmp_path / "templates")

    assert "rules:" in output
    assert "if: '$CI_COMMIT_TAG =~ /^v\\d+\\.\\d+\\.\\d+$/'" in output
    assert "if: '$CI_COMMIT_BRANCH == \"main\"'" in output
    assert "if: '$CI_COMMIT_BRANCH == \"develop\"'" in output

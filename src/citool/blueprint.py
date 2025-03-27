import json
from typing import Dict
import yaml
import sys

from pathlib import Path

from citool.config import Config
from citool.util.util import ask
from citool.util.langmap import detect_languages


def load_or_generate_blueprint(path: Path, config: Config) -> Dict:
    for ext in ("yaml", "yml", "json"):
        file = path / f"blueprint.{ext}"
        if file.exists():
            print(f"Loading existing blueprint from {file}")
            with open(file, "r") as f:
                return yaml.safe_load(f) if ext in ("yaml", "yml") else json.load(f)

    print("No blueprint found. Detecting project stack...")
    blueprint = detect_stack(path)
    if blueprint is None:
        if not ask(
            "Unable to detect language/build system. Create a minimal empty blueprint?"
        ):
            print("Aborting.")
            sys.exit(1)
        blueprint = {
            "language": "unknown",
            "build_system": "none",
            "build_commands": [],
        }

    blueprint["ci"] = config.ci
    blueprint["env"] = config.env

    if config.dry_run:
        print("--- Generated Blueprint ---")
        print(yaml.dump(blueprint, sort_keys=False))
    else:
        if ask("Create blueprint.yaml now?"):
            file = path / "blueprint.yaml"
            with open(file, "w") as f:
                yaml.dump(blueprint, f, sort_keys=False)
            print(f"Blueprint written to {file}")

    return blueprint


def detect_stack(path: Path) -> Dict | None:
    languages = detect_languages(path)

    if not languages:
        print("No known languages detected.")
        return None

    primary = languages[0]
    blueprint = {
        "language": primary.lower(),
        "build_system": "none",
        "build_commands": [],
    }

    if primary == "C":
        if (path / "Makefile").exists():
            blueprint["build_system"] = "make"
            blueprint["build_commands"] = ["make"]
    elif primary == "Python":
        if (path / "pyproject.toml").exists():
            blueprint["build_system"] = "poetry"
            blueprint["build_commands"] = ["poetry install"]
        elif (path / "setup.py").exists():
            blueprint["build_system"] = "setuptools"
            blueprint["build_commands"] = ["python setup.py install"]
    elif primary == "Java":
        if (path / "pom.xml").exists():
            blueprint["build_system"] = "maven"
            blueprint["build_commands"] = ["mvn clean package"]
        elif (path / "build.gradle").exists():
            blueprint["build_system"] = "gradle"
            blueprint["build_commands"] = ["gradle build"]

    print(f"Detected language: {primary}")
    print(f"Build system: {blueprint['build_system']}")

    return blueprint

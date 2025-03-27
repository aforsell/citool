import os
import subprocess
import yaml

from pathlib import Path
from typing import Dict, List


def load_extension_map() -> Dict[str, str]:
    path = Path(__file__).parents[1] / "vendor" / "languages.yml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    mapping: Dict[str, str] = {}
    for lang, meta in data.items():
        for ext in meta.get("extensions", []):
            mapping[ext.lstrip(".")] = lang
    return mapping


EXTENSION_MAP: Dict[str, str] = load_extension_map()


def has_linguist() -> bool:
    # NOTE: This approach assumes the 'linguist' gem is globally available,
    # but GitHub's official gem is not published to RubyGems by design.
    # It must be used via Bundler from the GitHub repository.
    #
    # I kinda forgot about that when writing this, so this isn’t tested
    # and probably won’t work out of the box. I left it here to show the initial idea.
    return False

    try:
        subprocess.run(
            ["ruby", "-e", "require 'linguist'; puts Linguist::VERSION"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def detect_with_linguist(path: Path) -> List[str]:
    # NOTE: See above
    return []
    try:
        result = subprocess.run(
            [
                "ruby",
                "-r",
                "linguist",
                "-e",
                f'puts Linguist::Repository.new("{path.resolve()}").languages.keys',
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception as e:
        print(f"Failed to run Linguist: {e}")
        return []


def detect_from_extensions(path: Path, mapping: Dict[str, str]) -> List[str]:
    special_files = {
        "Makefile": "C",
        "pom.xml": "Java",
        "build.gradle": "Java",
        "setup.py": "Python",
        "pyproject.toml": "Python",
    }

    detected = set()

    for root, dirs, files in os.walk(path):
        for file in files:
            ext = Path(file).suffix.lstrip(".").lower()
            name = Path(file).name
            if name in special_files:
                detected.add(special_files[name])
            elif ext in mapping:
                detected.add(mapping[ext])

    return sorted(detected)


def detect_languages(path: Path) -> List[str]:
    if has_linguist():
        return detect_with_linguist(path)

    print("Linguist not available, falling back to extension-based detection.")
    return detect_from_extensions(path, EXTENSION_MAP)

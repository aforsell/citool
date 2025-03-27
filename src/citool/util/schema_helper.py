import json
from pathlib import Path
from typing import List


def load_enum_choices(schema_path: Path, property_path: str) -> List[str]:
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    parts = property_path.split(".")
    current = schema.get("properties", {})

    for part in parts:
        current = current.get(part)
        if current is None:
            raise ValueError(f"Property '{property_path}' not found in schema")
        if "properties" in current:
            current = current["properties"]

    if "enum" not in current:
        raise ValueError(f"No enum found for property '{property_path}'")

    return current["enum"]


def load_examples(schema_path: Path, property_name: str) -> List[str]:
    with open(schema_path) as f:
        schema = json.load(f)
    prop = schema.get("properties", {}).get(property_name, {})
    return prop.get("examples", [])


def get_output_path_for_platform(schema_path: Path, platform: str) -> str:
    with open(schema_path, "r") as f:
        schema = json.load(f)

    ci_props = schema["properties"]["ci"]["properties"]
    platform_enum = ci_props["platform"]["enum"]

    if platform not in platform_enum:
        raise ValueError(f"Unknown CI platform: '{platform}'")

    # In current schema, there's only one output_path per platform
    # so we return a hardcoded map for now
    default_paths = {"gitlab": ".gitlab-ci.yml", "github": ".github/workflows/ci.yml"}

    if platform not in default_paths:
        raise ValueError(f"No default output path defined for platform: '{platform}'")

    return default_paths[platform]

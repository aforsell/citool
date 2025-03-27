from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from citool.config import Config
from citool.util.schema_helper import get_output_path_for_platform


DEFAULT_TEMPLATE_ROOT = Path(__file__).parent / "templates"


def render_template(
    blueprint: dict, config: Config, template_root: Path = DEFAULT_TEMPLATE_ROOT
) -> str:
    ci = config.ci
    env_name = config.env
    template_set = config.template or "base"
    language = blueprint["language"]

    relative_path = Path(ci) / template_set / f"{language}-{env_name}.yml.j2"

    jinja_env = Environment(
        loader=FileSystemLoader(template_root), trim_blocks=True, lstrip_blocks=True
    )

    try:
        template = jinja_env.get_template(str(relative_path))
    except TemplateNotFound as e:
        raise FileNotFoundError(f"Template missing in Jinja: {e.name}")

    return template.render(blueprint)


def get_output_path(config: Config, blueprint: dict) -> Path:
    if isinstance(blueprint["ci"], dict) and "output_path" in blueprint["ci"]:
        return config.path / blueprint["ci"]["output_path"]

    schema_path = Path(__file__).parent / "schemas" / "blueprint.schema.json"
    platform = (
        blueprint["ci"]["platform"]
        if isinstance(blueprint["ci"], dict)
        else blueprint["ci"]
    )
    output_path = get_output_path_for_platform(schema_path, platform)
    return config.path / output_path

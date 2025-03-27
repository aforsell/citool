import argparse
from pathlib import Path
import sys
import logging

from citool.config import Config
from citool.util.schema_helper import load_enum_choices, load_examples
from citool.blueprint import load_or_generate_blueprint
from citool.renderer import get_output_path, render_template


SCHEMA_PATH = Path(__file__).parent / "schemas" / "blueprint.schema.json"
CI_CHOICES = load_enum_choices(SCHEMA_PATH, "ci.platform")
RECOMMENDED_ENVS = load_examples(SCHEMA_PATH, "env")

logger = logging.getLogger("citool")
logging.basicConfig(level=logging.INFO)


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="citool: CI/CD pipeline generator")

    parser.add_argument(
        "path", nargs="?", type=Path, default=Path("."), help="Target project directory"
    )
    parser.add_argument(
        "--ci", choices=CI_CHOICES, help="Target CI platform (required)"
    )
    parser.add_argument("--env", help="Deployment environment (required)")
    parser.add_argument("--template", help="Custom template set name (e.g., team_xyz)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Render but do not write files"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing output"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    missing = []
    if not args.ci:
        missing.append("--ci")
    if not args.env:
        missing.append("--env")

    if missing:
        print(
            f"Error: Missing required argument(s): {', '.join(missing)}",
            file=sys.stderr,
        )
        print(f"Available CI platforms: {', '.join(CI_CHOICES)}")
        print(f"Recommended environments: {', '.join(RECOMMENDED_ENVS)}")
        sys.exit(1)

    config = Config(
        ci=args.ci,
        env=args.env,
        template=args.template,
        path=args.path,
        dry_run=args.dry_run,
        force=args.force,
        verbose=args.verbose,
    )

    if config.verbose:
        logger.setLevel(logging.DEBUG)

    if config.env not in RECOMMENDED_ENVS:
        print(f"Note: '{config.env}' is not a recommended environment.")
        print(f"Suggested environments: {', '.join(RECOMMENDED_ENVS)}")

    logger.debug("Parsed config: %s", vars(config))

    return config


def main() -> None:
    config = parse_args()
    logger.debug("Running citool with config: %s", vars(config))

    blueprint = load_or_generate_blueprint(config.path, config)
    output = render_template(blueprint, config)
    output_path = get_output_path(config, blueprint)

    if output_path.exists() and not config.force:
        print(f"Pipeline already exists: {output_path}. Use --force to overwrite.")
        sys.exit(1)

    if config.dry_run:
        print("--- Rendered Pipeline ---")
        print(output)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output)
        print(f"Pipeline written to {output_path}")


if __name__ == "__main__":
    main()

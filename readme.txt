citool
======

citool is a CI/CD pipeline generator designed to simplify and standardize the creation
of CI configurations for projects based on language and environment. It uses declarative
blueprint files to render CI pipelines using Jinja2 templates for GitLab, GitHub Actions,
or other systems.

-------------------------------------------------------------------------------
FEATURES
-------------------------------------------------------------------------------

- AUTOMATIC STACK DETECTION
  Detects programming language and build system from project contents using
  GitHub Linguist (if available) or a reliable extension/filename heuristic
  fallback. Supports Makefiles, pyproject.toml, pom.xml, etc.

- BLUEPRINT-DRIVEN PIPELINE GENERATION
  Uses simple, declarative blueprint files (YAML or JSON) that describe your
  project’s CI/CD needs (language, build system, test/lint/deploy commands).
  These blueprints are validated against a strict JSON Schema.

- TEMPLATE-BASED OUTPUT
  Uses Jinja2 templates to render CI configuration files for GitLab or GitHub
  Actions, with full customization per language, environment, and template set.
  Templates can include logic for deployment, branching, tagging, and more.

- DEPLOYMENT STRATEGIES
  Supports multiple deployments per blueprint, using:
    - Docker: builds and pushes container images
    - SSH: runs remote shell commands on a server
    - Rsync: uploads artifacts to target paths

- BRANCHING & TAGGING STRATEGIES
  Encourages Git best practices using CI template logic based on:
    - GitFlow or GitHub flow patterns
    - Protected branch enforcement
    - Release naming via semantic, calendar, or incremental tags

- ADVANCED PIPELINE LOGIC
  Blueprints can define:
    - Caching behavior and paths
    - Incremental build triggers
    - Artifact paths to preserve
    - Custom test/lint/scan stages

- SCHEMA-ENFORCED BEST PRACTICES
  Everything is driven by a versioned JSON Schema (draft 2020-12). It defines:
    - Available languages, platforms, build systems
    - Conditional rules for deployment methods
    - Output paths per CI platform
    - Examples and recommendations (e.g., environments)

- USER-TEMPLATES & EXTENSIBILITY
  Teams can define their own templates in `user_templates/`, structured the
  same way as the default ones. These override the default “base” templates.

- FULL CONTROL WITH MINIMAL SETUP
  Command-line interface accepts:
    --ci, --env, --template, --dry-run, --force, and more
  You can auto-generate blueprints or write your own.
  CI output paths are defined in the blueprint (not hardcoded).

- DRY-RUN, VERBOSE, AND SAFE DEFAULTS
  Preview rendered output with `--dry-run`
  Never overwrite existing files unless `--force` is used
  Logs and diagnostics printed separately from user output

- BUILT FOR EXTENSION
  Architecture supports:
    - Future CI platforms
    - Ability to convert pipelines from another CI platfoms (e.g., Jenkins)
    - More granular template logic
    - Modular schema updates via `$defs`

-------------------------------------------------------------------------------
QUICK START
-------------------------------------------------------------------------------

1. Install dependencies:

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

2. Create a project or navigate to an existing one:

    make setup-test-project

3. Generate a CI pipeline:

    bin/citool --ci gitlab --env dev path/to/project

    (Use --dry-run to preview without writing files.)

-------------------------------------------------------------------------------
BLUEPRINTS
-------------------------------------------------------------------------------

Blueprints define the build, test, linting, and deployment logic for a project.
They can be auto-detected or manually written.

Example blueprint.yaml:

language: python
build_system: setuptools
build_commands:
  - python setup.py install
test_commands:
  - pytest
lint_commands:
  - ruff check .
static_analysis_commands:
  - bandit -r src
security_scan_commands:
  - pip-audit

artifacts:
  paths:
    - dist/
    - build/

deployments:
  - method: ssh
    target_server: prod.example.com
    target_path: /opt/myapp/
    deploy_user: deploy
    commands:
      - systemctl restart myapp

caching:
  enabled: true
  paths:
    - .venv/
    - __pycache__/
  key: python-cache

incremental_build:
  enabled: true
  trigger_paths:
    - src/
    - tests/

branching:
  strategy: gitflow
  protected_branches:
    - main
    - dev
  release_branch_pattern: release/*

tagging:
  scheme: semantic
  prefix: v

ci:
  platform: gitlab
  output_path: .gitlab-ci.yml

env: dev

-------------------------------------------------------------------------------
TEMPLATE STRUCTURE
-------------------------------------------------------------------------------

Templates are Jinja2 files that define the final CI configuration. They're located in:

    src/citool/templates/<ci>/<template_set>/<language>-<env>.yml.j2

Example:

    src/citool/templates/gitlab/base/python-dev.yml.j2

User-defined templates can be added under user_templates/ with the same structure.

-------------------------------------------------------------------------------
DEPLOYMENT SUPPORT
-------------------------------------------------------------------------------

Multiple deployment methods are supported:

- docker : push image to registry
- rsync  : copy artifacts to server
- ssh    : run commands remotely

Defined in the 'deployments:' section of the blueprint.

-------------------------------------------------------------------------------
SCHEMA
-------------------------------------------------------------------------------

Blueprints are validated using a JSON Schema located at:

    src/citool/schemas/blueprint.schema.json

This ensures correct structure and offers editor integration.

-------------------------------------------------------------------------------
MAKE TARGETS
-------------------------------------------------------------------------------

    make install              Set up Python virtual environment
    make lint                 Run ruff against codebase
    make format               Run ruff format against codebase
    make test                 Run full test suite with coverage
    make run                  Show help
    make clean                Clean caches and coverage reports
    make setup-test-project   Create example project to test manually
    make clean-test-project   Remove the example project

-------------------------------------------------------------------------------
NOTES
-------------------------------------------------------------------------------

- GitHub Linguist support requires Ruby and the 'linguist' gem (not published to RubyGems).
    - Use of linguist requires further implementation
- Recommended environments and CI platforms are validated but customizable.
- The tool assumes Jinja2 template filenames match the structure:
      <language>-<env>.yml.j2

-------------------------------------------------------------------------------
HOW IT WORKS
-------------------------------------------------------------------------------

1. Detect Project Stack

    - If no blueprint.yaml/json exists:
        - Try GitHub Linguist (if available)
        - Fall back to file extension / filename heuristics

2. Load or Generate Blueprint

    - Load existing blueprint.yaml or blueprint.json
    - If none exists, detect language/build system and offer to create one

3. Render CI Pipeline

    - Use selected CI platform and environment
    - Load the matching Jinja2 template
    - Fill it in with blueprint data

4. Write CI Configuration

    - Output file path is defined in blueprint's 'ci.output_path'
    - Will not overwrite existing file unless --force is used

-------------------------------------------------------------------------------
KEY CONCEPTS
-------------------------------------------------------------------------------

Schema
    - Defines the rules
    - Stored in: src/citool/schemas/blueprint.schema.json
    - Used for validation, suggestion, and CLI argument checking

Blueprint
    - Defines what should happen
    - Stored in: blueprint.yaml or blueprint.json
    - Provides data like language, build system, commands, etc.

Template
    - Defines how the CI config is rendered
    - Stored in: src/citool/templates/<ci>/<template_set>/<language>-<env>.yml.j2
    - Customizable for team, use case, or environment

Configuration hierarchy

            +---------------+
            |   Schema      |
            | (JSON-Schema) |
            +---------------+
                 | defines rules for
        +--------v---------+
        |   Blueprint      |
        | (blueprint.yaml) |
        +----┬-------------+
             | provides data for
      +------v----------------+
      |      Template         |
      | (Jinja2 .yml.j2 file) |
      +----┬-----------------++
           | renders
   +-------v--------------------+
   |  CI Config Output (.yml)   |
   | (e.g. .gitlab-ci.yml)      |
   +----------------------------+

-------------------------------------------------------------------------------
WORKFLOW SUMMARY
-------------------------------------------------------------------------------

             +----------------------+
             |      Run citool      |
             +----------+-----------+
                        |
         +--------------v---------------+
         |   Does blueprint exist?      |
         +---------+---------+----------+
                   |         |
         +---------v--+   +--v----------------------+
         |    Yes     |   |  No                     |
         |    Load    |   |  Detect stack           |
         +------------+   |  Ask to write           |
                          +----------+--------------+
                                     |
                +--------------------v------------------+
                |  User accepts?  |  User declines?     |
                |  -> Write file  |  -> Abort / minimal |
                +--------+--------+---------------------+
                         |
              +----------v--------------+
              |  Select Jinja2 template |
              |  based on:              |
              |    - CI platform        |
              |    - environment        |
              |    - language           |
              +----------+--------------+
                         |
                 +-------v-------+
                 | Render output |
                 +-------+-------+
                         |
               +---------v-----------+
               | Write to output     |
               | (or dry-run only)   |
               +---------------------+

-------------------------------------------------------------------------------
LICENSE
-------------------------------------------------------------------------------

UNLICENSE — public domain

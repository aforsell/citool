from pathlib import Path


class Config:
    def __init__(
        self,
        ci: str,
        env: str,
        template: str | None = None,
        path: Path = Path("."),
        dry_run: bool = False,
        force: bool = False,
        verbose: bool = False,
    ):
        self.ci = ci
        self.env = env
        self.template = template
        self.path = path
        self.dry_run = dry_run
        self.force = force
        self.verbose = verbose

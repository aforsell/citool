def ask(prompt: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{prompt} {suffix} ").strip().lower()
    if not response:
        return default
    return response in ("y", "yes")

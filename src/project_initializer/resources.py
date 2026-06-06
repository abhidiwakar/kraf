from importlib.resources import files
from pathlib import Path


def builtin_pack_dirs() -> list[Path]:
    pack_root = files("project_initializer") / "packs"
    return sorted(Path(str(item)) for item in pack_root.iterdir() if item.is_dir())

from pathlib import Path
import yaml

def load_config(path: str | Path) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def save_config(cfg: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

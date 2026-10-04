import os
from pathlib import Path

THESIS_ROOT = Path(os.environ.get("THESIS_ROOT", "/content/drive/MyDrive/phd_thesis"))

def path(*parts) -> Path:
    """Build paths anchored to thesis root."""
    return THESIS_ROOT.joinpath(*parts)

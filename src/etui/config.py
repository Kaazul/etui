"""Handles config initialization and updates."""

from dataclasses import dataclass
from pathlib import Path
import shutil
import tomllib

from platformdirs import user_config_dir

from etui.file_utils import ROOT_PATH, PYTHON_UV

DEFAULT_CONFIG_DIR = ROOT_PATH / "config_defaults"

USER_CONFIG_DIR = Path(user_config_dir("etui"))

SETTINGS_FILE = "settings.toml"
SCRIPT_FOLDERS_FILE = "script_folders.toml"

@dataclass
class ScriptFolder:
    name: str
    path: Path
    executable: Path = PYTHON_UV
    cwd: Path = ROOT_PATH
    file_extension: str = ".py"
    exclude_start: tuple[str] = ("__",)


def ensure_user_configs():
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    for name in (SETTINGS_FILE, SCRIPT_FOLDERS_FILE):
        user = USER_CONFIG_DIR / name
        default = DEFAULT_CONFIG_DIR / name

        if not user.exists():
            shutil.copy(default, user)


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def load_settings() -> dict:
    return load_toml(USER_CONFIG_DIR / SETTINGS_FILE)


def load_script_folders() -> list[dict]:
    data = load_toml(USER_CONFIG_DIR / SCRIPT_FOLDERS_FILE)
    folders = data.get("folders", [])

    for folder in folders:
        folder["path"] = (ROOT_PATH / folder["path"]).resolve()
        folder["cwd"] = (ROOT_PATH / folder["cwd"]).resolve()
        folder["python"] = (ROOT_PATH / folder["python"]).resolve()

    return folders


class Config:
    def __init__(self):
        ensure_user_configs()
        self.settings = load_settings()
        self.script_folders = load_script_folders()

    @property
    def log_retention_days(self) -> int:
        return self.settings["logging"]["retention_days"]

    @property
    def log_dir(self) -> Path:
        return USER_CONFIG_DIR / self.settings["logging"]["log_dir"]

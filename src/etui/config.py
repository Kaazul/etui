"""Handles config initialization and updates."""

from dataclasses import dataclass
from pathlib import Path
import shutil
import tomllib

import tomli_w
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
    file_extension: str = "*.py"
    exclude_start: tuple[str] = ("_", ".")

    def to_toml_dict(self) -> dict[str, str | tuple[str]]:
        """Returns dict for saving to toml."""
        return {
            "name": self.name,
            "path": str(self.path),
            "executable": str(self.executable),
            "cwd": str(self.cwd),
            "file_extension": self.file_extension,
            "exclude_start": self.exclude_start,
        }


def ensure_user_configs():
    """Ensures that the user config files are present."""
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    for name in (SETTINGS_FILE, SCRIPT_FOLDERS_FILE):
        user_config = USER_CONFIG_DIR / name
        default_config = DEFAULT_CONFIG_DIR / name
        if not user_config.exists():
            shutil.copy(default_config, user_config)


def restore_default_script_folders():
    """Restores default script folders.

    CAVEAT: This overwrites the config script folder."""
    user_config = USER_CONFIG_DIR / SCRIPT_FOLDERS_FILE
    default_config = DEFAULT_CONFIG_DIR / SCRIPT_FOLDERS_FILE
    shutil.copy(default_config, user_config)


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def load_settings() -> dict:
    return load_toml(USER_CONFIG_DIR / SETTINGS_FILE)


def load_script_folders() -> dict[str, ScriptFolder]:
    toml_folders = load_toml(USER_CONFIG_DIR / SCRIPT_FOLDERS_FILE).get("folders", [])
    folders = {}
    for folder in toml_folders:
        if not folder["file_extension"].startswith("*"):
            folder["file_extension"] = "*" + folder["file_extension"]
        folders[folder["name"]] = ScriptFolder(
            folder["name"],
            Path(folder["path"]),
            Path(folder["executable"]),
            folder["cwd"],
            folder["file_extension"],
            folder["exclude_start"],
        )
    return folders


def save_script_folders(
    folders: dict[str, ScriptFolder],
    file_path: Path = USER_CONFIG_DIR / SCRIPT_FOLDERS_FILE,
):
    """Saves script folders to a toml file."""
    folder_list = []
    for folder in folders.values():
        folder_list.append(folder.to_toml_dict())
    with file_path.open("wb") as f:
        tomli_w.dump({"folders": folder_list}, f)


class Config:
    def __init__(self):
        ensure_user_configs()
        self.settings = load_settings()
        self.script_folders = load_script_folders()
        self.log_retention_days = self.settings["logging"]["retention_days"]
        self.log_path = self.settings["logging"]["log_path"]
        self.theme = self.settings["tui"]["theme"]

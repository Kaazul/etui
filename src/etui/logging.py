"""Logger for the whole project."""

import logging
import time
from datetime import datetime
from pathlib import Path
from rich.text import Text

from etui.file_utils import LOG_PATH

LOG_COLORS = {
    "DEBUG": "dim cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "bold red",
    "CRITICAL": "bold red on black",
    "STDERR": "red",
}


def format_line(text: str, is_stderr=False) -> Text:
    timestamp = datetime.now().strftime("%H:%M:%S")
    level = None
    for lvl in LOG_COLORS:
        if text.startswith(lvl):
            level = lvl
            break
    style = LOG_COLORS.get(level, LOG_COLORS["STDERR"] if is_stderr else None)
    line = Text(f"[{timestamp}] ", style="dim")
    line.append(text.rstrip(), style=style)
    return line


def create_log_file(script_path: Path, logs_root: Path = LOG_PATH) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = script_path.stem
    log_dir = logs_root / script_path.parent.name
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"{name}_{timestamp}.log"


def get_logger(log_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("etui")
    logger.setLevel(log_level)
    return logger


def cleanup_old_logs(log_root: Path = LOG_PATH, max_age_days: int = 30):
    """Delete files in log_root older than max_days recursively."""
    if not log_root.exists():
        return
    cutoff = time.time() - (max_age_days * 86400)
    for path in log_root.rglob("*"):
        if path.is_file():
            try:
                if path.stat().st_mtime < cutoff:
                    path.unlink()
            except Exception as e:
                print(f"Failed to delete log {path}: {e}")

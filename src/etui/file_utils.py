"""Utility classes and functions for file reading and manipulation."""

from dataclasses import dataclass
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError


ETUI_PATH = Path(__file__).resolve().parent
ROOT_PATH = ETUI_PATH.parent.parent
TCSS_PATH = ETUI_PATH / "tcss"

TEST_PATH = ROOT_PATH / "tests"
LOG_PATH = ROOT_PATH / "log"

PYTHON_UV = ROOT_PATH / ".venv/bin/python"


@dataclass
class ParserArgument:
    name: str
    required: bool = False
    default: str | None = None
    action: str | None = None
    type: str = "str"
    help: str = ""


@dataclass
class Parser:
    name: str
    args: list[ParserArgument]


def get_version() -> str:
    """Reads the version of the etui project"""
    try:
        return version("etui")
    except PackageNotFoundError:
        return "unknown"


def extract_argparse(script_path: Path, multiple_parsers: bool = True) -> dict:
    """Extract argparse arguments from a script."""
    parsers = {}
    with open(script_path, "r") as file:
        lines = file.readlines()
    arg_lines = _argparse_helper(lines)
    # ToDo: Remove as soon as multiple parser problems is fixed:
    if not arg_lines:
        return parsers
    for line in arg_lines:
        parser_name = line.split(".")[0].lstrip()  # Get parser name
        if not parsers.get(parser_name):
            parsers[parser_name] = Parser(parser_name, [])
        arg_name, arg_required, arg_default = "", False, None
        arg_action, arg_type, arg_help = None, "str", ""
        params = line.split("(")[1].rstrip().rstrip(")").split(",")
        name_set = False  # There could be two names, e.g.: '-i, --ip'
        for param in params:
            if "=" in param:
                if "required" in param:
                    arg_required = True if "True" in param else False
                elif "default" in param:
                    arg_default = param.split("=")[1].strip().strip('"')
                elif "action" in param:
                    arg_action = param.split("=")[1].strip().strip('"')
                elif "help" in param:
                    arg_help = param.split("=")[1].strip().strip('"')
            else:
                if not name_set:
                    arg_name = param.strip().strip('"')
                    name_set = True
        parsers[parser_name].args.append(
            ParserArgument(
                arg_name, arg_required, arg_default, arg_action, arg_type, arg_help
            )
        )
    # ToDo: Remove as soon as multiple parser problem is fixed
    if not multiple_parsers:
        for value in parsers.values():
            return value
    return parsers


def _argparse_helper(lines: list[str]) -> list[str]:
    """Returns list of argparse arguments from a script in 1 line per argument.

    Due to file formatting it is possible that an argument is added to a parser in a
    python script in more than one line. This helper function returns all added arguments
    in 1 string per argument without a newline character."""
    arg_lines = []
    arg_parts = []  # For multi-line added args
    for line in lines:
        if "add_argument(" in line:
            if ")" in line:
                arg_lines.append(line)
            else:
                arg_parts.append(line)
        elif arg_parts:
            if ")" in line:
                arg_parts.append(line)
                arg_lines.append(" ".join(arg_parts))
                arg_parts = []
            else:
                arg_parts.append(line)
    return arg_lines

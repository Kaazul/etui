import asyncio
from io import TextIOWrapper
from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header,
    Footer,
    RichLog,
    Input,
    Button,
    Label,
    ListView,
    ListItem,
    Select,
    Checkbox,
    Static,
)
from textual.containers import Horizontal, Vertical, VerticalScroll

from etui.config import (
    load_script_folders,
    save_script_folders,
    ScriptFolder,
    restore_default_script_folders,
)
from etui.logging import create_log_file, format_line
from etui.file_utils import TCSS_PATH, extract_argparse, ROOT_PATH, PYTHON_UV, Parser
from etui.screen_helper import ArgFlagRow, ArgInputRow, QuestionScreen


class ScriptLauncher(Screen):
    CSS_PATH = str(TCSS_PATH / "scriptlauncher.tcss")
    BINDINGS = [
        ("ctrl+r", "run_script", "Run Script"),
        ("ctrl+c", "terminate_process", "Terminate"),
    ]

    def __init__(self, title: str = "Scriptlauncher") -> None:
        super().__init__()
        self.title = title
        self.process: asyncio.subprocess.Process | None = None
        self.script_folders = load_script_folders()
        self.folder_select = Select(
            options=[(name, name) for name in self.script_folders],
            value=list(self.script_folders.keys())[0],
            id="folder_select",
            allow_blank=False,
        )
        self.script_list = ListView(id="script_list")
        self.parser_panel = Horizontal(id="parser_panel")
        self.arg_panel = VerticalScroll(id="arg_panel")
        self.output_box = RichLog(id="output_box")
        self.input_box = Input(placeholder="Send input to script…", id="input_box")
        self.log_file_path: Path | None = None
        self.log_file: TextIOWrapper | None = None
        self._parsers: dict[str, Parser] = {}
        self.parser_select: Select | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal():
            # LEFT: script selector
            with Vertical(id="sidebar"):
                yield Label("Script Folder:")
                yield self.folder_select
                yield Label("Available Scripts:")
                yield self.script_list

            # RIGHT: arguments + output
            with Vertical(id="main"):
                yield self.parser_panel
                yield self.arg_panel
                with Horizontal():
                    yield Button("Run Script", variant="success", id="run_button")
                    yield Button("Clear Output", id="clear")
                    yield Button("Stop Script", variant="error", id="stop_button")
                yield self.output_box
                yield self.input_box
        yield Footer()

    async def on_mount(self):
        initial_folder = self.folder_select.value
        self.load_scripts_for_folder(initial_folder)
        self.script_list.focus()

    async def on_select_changed(self, event: Select.Changed):
        """Loads scripts when folder is selected."""
        if event.select is self.folder_select:
            self.load_scripts_for_folder(event.value)
        elif event.select is self.parser_select:
            await self.render_arguments(event.value)

    async def on_list_view_selected(self, message: ListView.Selected):
        """Gets and mounts arguments for chosen script."""
        await self.parser_panel.remove_children()
        item = message.item  # This is a ListItem
        script_path: Path = item.script_path
        self._parsers = extract_argparse(script_path)
        if not self._parsers:
            await self.arg_panel.mount(Label("No argparse arguments found."))
            return
        elif len(self._parsers) == 1:
            for parser_name in self._parsers:
                await self.render_arguments(parser_name)
                return
        self.parser_select = Select(
            options=[(parser_name, parser_name) for parser_name in self._parsers],
            value=list(self._parsers.keys())[0],
            allow_blank=False,
            id="parser_select",
        )
        await self.parser_panel.mount(Label("Command:"))
        await self.parser_panel.mount(self.parser_select)

    async def render_arguments(self, parser_name: str):
        await self.arg_panel.remove_children()  # Clear old args
        parser = self._parsers[parser_name]
        for arg in parser.args:
            if arg.action == "store_true":
                row = ArgFlagRow(arg.name)
            else:
                row = ArgInputRow(arg.name, arg.default)
            await self.arg_panel.mount(row)

    async def action_run_script(self):
        """Runs chosen script."""
        selected = self.script_list.index
        if selected is None:
            self.output_box.write("No script selected.", scroll_end=True)
            return

        item = self.script_list.children[selected]
        script_path: Path = item.script_path

        folder_name = self.folder_select.value
        python_exe = self.script_folders[folder_name].executable

        args = []
        for row in self.arg_panel.children:
            if hasattr(row, "get_value"):
                args.extend(row.get_value())

        cmd = [str(python_exe), "-u", str(script_path), *args]

        self.log_file_path = create_log_file(script_path)
        self.log_file = open(self.log_file_path, "w", encoding="utf-8")

        self.output_box.write(f"Logging to: {self.log_file_path}", scroll_end=True)
        output = f"Running: {' '.join(cmd)}"
        self._output_and_log(output)
        self.input_box.disabled = False

        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self.run_worker(self.read_stream(self.process.stdout), exclusive=False)
        self.run_worker(
            self.read_stream(self.process.stderr, is_stderr=True), exclusive=False
        )
        # Worker for outside of script logging and exit handling
        self.run_worker(self.wait_for_exit(), group="process")

    async def read_stream(self, stream, is_stderr=False):
        """Reads the output stream in a subprocess."""
        while True:
            line = await stream.readline()
            if not line:
                break

            text = line.decode(errors="replace")
            self._output_and_log(text, is_stderr=is_stderr)

    async def on_input_submitted(self, event: Input.Submitted):
        """Sends input to script."""
        if not self.process or self.process.returncode is not None:
            return

        text = event.value + "\n"
        self.process.stdin.write(text.encode())
        await self.process.stdin.drain()
        event.input.clear()

    async def wait_for_exit(self):
        """Handles events of script/process finishing.

        Gets the exit code to print it to the output box and log file. Closes log file,
        deletes process object and disables
        the input box."""
        return_code = await self.process.wait()
        output = f"✔ Script finished (exit code {return_code})"
        log_text = "=== SCRIPT FINISHED ===\n"
        self._output_and_log(output, log_text)
        self.input_box.disabled = True
        self.process = None

    async def action_terminate_process(self):
        """Terminates script by sending SIGTERM."""
        if not self.process:
            return
        output = "User interrupt. Sending SIGTERM to script process."
        self._output_and_log(output)
        try:
            self.process.terminate()
        except AttributeError:
            pass

    async def on_button_pressed(self, event: Button.Pressed):
        """Handles all buttons in event of them being pressed."""
        if event.button.id == "run_button":
            await self.action_run_script()
        elif event.button.id == "clear":
            self.output_box.clear()
        elif event.button.id == "stop_button":
            await self.action_terminate_process()

    def load_scripts_for_folder(self, folder_name: str):
        """Loads and displays all py scripts in chosen folder.

        Excludes py scripts starting with chars defined in ScriptFolder.exclude_start."""
        self.script_list.clear()
        script_folder = self.script_folders[folder_name]
        if not script_folder.path.exists():
            return
        for script in sorted(script_folder.path.glob(script_folder.file_extension)):
            if script.name[0] in script_folder.exclude_start:
                continue
            item = ListItem(Label(script.name))
            item.script_path = script
            self.script_list.append(item)

    def _output_and_log(
        self, output: str, log_text: str | None = None, is_stderr: bool = False
    ) -> None:
        rich_text = format_line(output, is_stderr=is_stderr)
        if not log_text:
            log_text = str(rich_text)
        self.output_box.write(rich_text, scroll_end=True)
        self.log_file.write(log_text + "\n")
        self.log_file.flush()


class ScriptFolderManager(Screen):
    """Reusable widget for managing script folders."""

    def __init__(self, title: str = "ScriptFolder Manager") -> None:
        super().__init__()
        self.title = title
        self.script_folders = load_script_folders()
        self.folder_list_view = ListView()
        self._folder_list: list[ScriptFolder] = []
        self.name_input = Input(placeholder="Name")
        self.path_input = Input(placeholder="Folder path")

        self.python_input = Input(placeholder="Python executable (optional)")

        self.cwd_checkbox = Checkbox(
            "Check, if working directory should be folder path",
            value=True,
        )

    def compose(self):
        yield Header(show_clock=True)
        yield Static("Script Folders", classes="title")
        yield self.folder_list_view
        yield Static("Add Script Folder", classes="subtitle")
        yield self.name_input
        yield self.path_input
        yield self.python_input
        yield self.cwd_checkbox
        with Horizontal():
            yield Button("Add", id="add", variant="success")
            yield Button("Remove Selected", id="remove", variant="error")
            yield Button("Restore Default", id="default", variant="warning")
        yield Footer()

    async def on_mount(self):
        self.refresh_folder_list()

    def refresh_folder_list(self):
        self.folder_list_view.clear()

        for folder in load_script_folders().values():
            label = f"{folder.name}  →  {folder.path}"
            self.folder_list_view.append(ListItem(Label(label)))
            self._folder_list.append(folder)

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add":
            self._add_folder()

        elif event.button.id == "remove":
            self._check_remove_selected()

        elif event.button.id == "default":
            self._check_restore_default()

    def _add_folder(self):
        name = self.name_input.value.strip()
        path = self.path_input.value.strip()
        python = self.python_input.value.strip()

        python = python or str(PYTHON_UV)

        cwd = path if self.cwd_checkbox.value else ROOT_PATH

        folders = load_script_folders()
        if name in folders:
            raise Exception(f"Folder {name} already exists")
        folders[name] = ScriptFolder(name, path, python, cwd)
        save_script_folders(folders)
        self.refresh_folder_list()
        self._clear_inputs()

    def _check_remove_selected(self):
        msg = "Please confirm if you want to remove the folder"

        self.app.push_screen(
            QuestionScreen(msg, yes_variant="error", no_variant="primary"),
            self._remove_selected_folder,
        )

    def _remove_selected_folder(self, is_confirmed: bool = False):
        if is_confirmed:
            index = self.folder_list_view.index
            if index is None:
                return
            folders = load_script_folders()
            folders.pop(self._folder_list[index].name)
            save_script_folders(folders)
        self.refresh_folder_list()

    def _check_restore_default(self):
        msg = (
            "Are you sure to restore default folders?\n"
            "This will delete all added folders from the folder list"
        )
        self.app.push_screen(
            QuestionScreen(msg, yes_variant="error", no_variant="primary"),
            self._restore_default,
        )

    def _restore_default(self, is_confirmed: bool = False):
        if is_confirmed:
            restore_default_script_folders()
        self.refresh_folder_list()

    def _clear_inputs(self):
        self.name_input.value = ""
        self.path_input.value = ""
        self.python_input.value = ""
        self.cwd_checkbox.value = True

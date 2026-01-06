"""Small screen classes."""

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Static, Button, Label, MarkdownViewer, Header, Input, Checkbox
from textual.containers import Vertical, Grid

class ArgInputRow(Static):
    """One input row for a single CLI argument."""

    def __init__(self, arg_name: str, default=None):
        super().__init__()
        self.arg_name = arg_name
        self.default = default

    def compose(self):
        yield Label(f"{self.arg_name}:")
        yield Input(value=self.default or "")

    def get_value(self):
        input_widget = self.query_one(Input)
        text = input_widget.value.strip()
        if text:
            return [self.arg_name, text]
        return []


class ArgFlagRow(Static):
    """For flags with action='store_true' or 'store_false'."""

    def __init__(self, arg_name: str):
        super().__init__()
        self.arg_name = arg_name

    def compose(self):
        yield Checkbox(self.arg_name)
        yield Label()

    def get_value(self):
        checkbox = self.query_one(Checkbox)
        return [self.arg_name] if checkbox.value else []


class QuitScreen(ModalScreen[bool]):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.dismiss(True)
        else:
            self.dismiss(False)


class InfoScreen(Screen):
    def __init__(self, file_path: Path, title: str = "Info") -> None:
        super().__init__()
        self.file_path = file_path
        self.title = title
        with open(self.file_path, "r", encoding="utf-8") as file:
            self.md_content = file.read()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name=self.title, id=self.title)
        markdown_viewer = MarkdownViewer(self.md_content, show_table_of_contents=True)
        markdown_viewer.code_indent_guides = False
        yield markdown_viewer


class NotImplementedScreen(Screen):
    """Placeholder Screen for not yet implemented functionalities."""
    def __init__(self, title: str = "Not Implemented") -> None:
        super().__init__()
        self.title = title

    def compose(self):
        with Vertical(id="not-implemented"):
            yield Static(
                f"{self.title}\n\nThis functionality is not implemented yet.",
                id="message",
            )
            yield Button("Back", id="back")

    def on_mount(self) -> None:
        self.query_one("#back", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.action_back()

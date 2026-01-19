"""Small screen classes."""

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import (
    Static,
    Button,
    Label,
    MarkdownViewer,
    Header,
    Input,
    Checkbox,
    Footer,
)
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


class QuestionScreen(ModalScreen[bool]):
    """Screen with a dialog to ask yes/no questions."""

    BUTTON_VARIANTS = ["default", "primary", "success", "warning", "error"]

    def __init__(
        self,
        question: str = "Are you sure?",
        yes: str = "Confirm",
        yes_variant="success",
        no: str = "Cancel",
        no_variant: str = "error",
    ) -> None:
        """Screen with a dialog to ask yes/no questions.

        Attributes
        ----------
        question
            defines the question that is displayed
        yes
            defines the name displayed on the confirmation button
        yes_variant
            defines the Button.variant (design) of the confirmation button
        no
            the name displayed on the cancel button
        no_variant
            defines the Button.variant (design) of the cancel button"""
        super().__init__()
        self._question = question
        self._yes = yes
        self._yes_variant = (
            yes_variant if yes_variant in self.BUTTON_VARIANTS else "success"
        )
        self._no = no
        self._no_variant = no_variant if no_variant in self.BUTTON_VARIANTS else "error"

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self._question, id="question"),
            Button(self._yes, variant=self._yes_variant, id="yes"),
            Button(self._no, variant=self._no_variant, id="no"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)


class InfoScreen(Screen):
    BINDINGS = [
        ("f", "toggle_toc", "Toggle TOC"),
    ]

    def __init__(self, file_path: Path, title: str = "Info") -> None:
        super().__init__()
        self.file_path = file_path
        self.title = title
        with open(self.file_path, "r", encoding="utf-8") as file:
            self.md_content = file.read()
        self.md_viewer = MarkdownViewer(self.md_content, show_table_of_contents=True)
        self.md_viewer.code_indent_guides = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name=self.title, id=self.title)
        yield self.md_viewer
        yield Footer()

    def action_toggle_toc(self) -> None:
        self.md_viewer.show_table_of_contents = (
            not self.md_viewer.show_table_of_contents
        )


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

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer
from textual.containers import Vertical
from textual.reactive import reactive

from etui.config import ensure_user_configs
from etui.scriptlauncher import ScriptLauncher, ScriptFolderManager
from etui.screen_helper import NotImplementedScreen, QuestionScreen, InfoScreen
from etui.file_browser import FileBrowser
from etui.file_utils import ETUI_PATH, LOG_PATH, TCSS_PATH, get_version
from etui.logging import cleanup_old_logs

README_PATH = ETUI_PATH / "README.md"


class MainScreen(Screen):
    """Main application menu."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="menu"):
            yield Button("ScriptLauncher", id="scriptlauncher")
            yield Button("LogViewer", id="logview")
            yield Button("ScriptFolder Manager", id="foldermanager")
            yield Button("Settings", id="settings")
            yield Button("Info", id="info")
        yield Footer()

    def on_mount(self) -> None:
        """Defines what happens when the screen is mounted/installed."""
        first_button = self.query_one("#scriptlauncher", Button)
        first_button.focus()

    def action_focus_next(self) -> None:
        self.focus_next()

    def action_focus_previous(self) -> None:
        self.focus_previous()

    def action_activate(self) -> None:
        focused = self.focused
        if isinstance(focused, Button):
            focused.press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "scriptlauncher":
            self.app.push_screen(ScriptLauncher())
        elif button_id == "info":
            self.app.push_screen(InfoScreen(README_PATH))
        elif button_id == "logview":
            self.app.push_screen(FileBrowser(LOG_PATH))
        elif button_id == "foldermanager":
            self.app.push_screen(ScriptFolderManager())
        else:
            self.app.push_screen(NotImplementedScreen(title=event.button.label))


class ETui(App):
    CSS_PATH = str(TCSS_PATH / "tui.tcss")
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("up", "focus_previous", "Focus previous"),
        ("down", "focus_next", "Focus next"),
        ("enter", "activate", "Activate"),
        ("escape", "back", "Back"),
    ]

    running_scripts = reactive(dict)

    def __init__(self):
        super().__init__()
        ensure_user_configs()
        self.title = "ETUI"
        self.sub_title = get_version()

    async def on_mount(self) -> None:
        cleanup_old_logs()
        await self.push_screen(MainScreen())

    def action_back(self) -> None:
        if len(self.app.screen_stack) > 2:  # Avoid popping Main Screen
            self.app.pop_screen()

    def action_request_quit(self) -> None:
        """Displays the quit screen."""

        def check_quit(is_quit: bool | None) -> None:
            """Called when Quitscreen is dismissed."""
            if is_quit:
                self.exit()

        self.push_screen(
            QuestionScreen(
                "Do you really want to quit?", yes_variant="error", no_variant="primary"
            ),
            check_quit,
        )


def main():
    """Sets up and runs the TUI."""
    ETui().run()


if __name__ == "__main__":
    main()

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header,
    Footer,
    Label,
    Select,
)
from textual.containers import Horizontal, Vertical

from etui.config import Config


class SettingsScreen(Screen):
    """Application settings screen with categories."""

    def __init__(self, title: str = "Settings"):
        super().__init__()
        self.title = title
        self.config = Config()
        self.theme_select = Select(
            options=[(theme, theme) for theme in self.app.available_themes],
            value=self.app.theme,
            id="theme-select",
        )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="settings-panel"):
            with Vertical(id="graphics-panel"):
                yield Label("App Theme")
                yield self.theme_select
            with Vertical(id="logging-panel"):
                yield Label("logging")
        yield Footer()

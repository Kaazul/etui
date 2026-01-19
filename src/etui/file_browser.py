"""FileBrowser based on the code browser example in the textualize repo."""

from pathlib import Path

from rich.traceback import Traceback
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.highlight import highlight
from textual.reactive import var, reactive
from textual.screen import Screen
from textual.widgets import DirectoryTree, Footer, Header, Static

from etui.file_utils import ROOT_PATH, TCSS_PATH


class FileBrowser(Screen):
    """FileBrowser app."""

    CSS_PATH = str(TCSS_PATH / "file_browser.tcss")
    BINDINGS = [
        ("f", "toggle_files", "Toggle Files"),
        ("q", "quit", "Quit"),
    ]

    show_tree = var(True)
    path: reactive[str | None] = reactive(None)

    def __init__(self, path: Path | str = ROOT_PATH) -> None:
        super().__init__()
        self.root_path = str(path)

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        path = self.root_path
        yield Header(show_clock=True)
        with Container():
            yield DirectoryTree(path, id="tree-view")
            with VerticalScroll(id="file-view"):
                yield Static(id="file", expand=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user clicks a file in the directory tree."""
        event.stop()
        self.path = str(event.path)

    def watch_path(self, path: str | None) -> None:
        """Called when path changes."""
        file_view = self.query_one("#file", Static)
        if path is None:
            file_view.update("")
            return
        try:
            file = Path(path).read_text(encoding="utf-8")
            syntax = highlight(file, path=path)
        except Exception:
            file_view.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"
        else:
            file_view.update(syntax)
            self.query_one("#file-view").scroll_home(animate=False)
            self.sub_title = path

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree

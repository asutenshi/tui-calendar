from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class DeleteConfirmDialog(ModalScreen[bool]):
    """Модальное окно для подтверждения удаления заметки."""

    CSS = """
    DeleteConfirmDialog {
        align: center middle;
        background: $background 50%;
    }

    #dialog-box {
        width: 40;
        height: 12;
        padding: 1 2;
        border: thick $error;
        background: $surface;
        align: center middle;
    }

    #dialog-message {
        content-align: center middle;
        text-align: center;
        height: 1fr;
        width: 100%;
        margin-bottom: 1;
    }

    #dialog-buttons {
        align: center middle;
        height: auto;
        width: 100%;
    }

    Button {
        min-width: 12;
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("h", "focus_left", "Left", show=False),
        Binding("l", "focus_right", "Right", show=False),
        Binding("escape", "dismiss_dialog", "Cancel", show=False),
    ]

    def __init__(self, note_title: str):
        super().__init__()
        self.note_title = note_title

    def compose(self) -> ComposeResult:
        with Grid(id="dialog-box"):
            yield Label(
                f"Are you sure you want to\ndelete '{self.note_title}'?", id="dialog-message"
            )
            with Horizontal(id="dialog-buttons"):
                yield Button("No", variant="primary", id="btn_no")
                yield Button("Yes", variant="error", id="btn_yes")

    def on_mount(self) -> None:
        self.query_one("#btn_no").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_dismiss_dialog(self) -> None:
        self.dismiss(False)

    def action_focus_left(self) -> None:
        self.query_one("#btn_no").focus()

    def action_focus_right(self) -> None:
        self.query_one("#btn_yes").focus()

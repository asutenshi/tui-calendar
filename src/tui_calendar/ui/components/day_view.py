from datetime import timedelta

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static


class DayView(Static):
    """Day View (To-Do list)."""

    can_focus = True

    BINDINGS = [
        Binding("h", "prev_day", "Prev Day", show=False),
        Binding("l", "next_day", "Next Day", show=False),
    ]

    DEFAULT_CSS = """
    DayView {
        width: 100%;
        height: 100%;
        border-top: solid $panel-lighten-3;  
        border-left: solid $panel-lighten-3; 
        align: center middle; /* Выравниваем внутренний блок по центру */
    }
    
    #day-content {
        content-align: center middle;
        width: auto;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(id="day-content")

    def on_mount(self) -> None:
        self.rebuild_day()

    def rebuild_day(self) -> None:
        selected = self.app.selected_date
        # Английский формат: "Saturday, 09 May 2026"
        header = selected.strftime("%A, %d %B %Y")

        content = f"📝 {header}\n\n[ mock tasks ]"
        self.query_one("#day-content", Static).update(content)

    def action_prev_day(self) -> None:
        self.app.selected_date -= timedelta(days=1)
        self.rebuild_day()

    def action_next_day(self) -> None:
        self.app.selected_date += timedelta(days=1)
        self.rebuild_day()

    def on_show(self) -> None:
        self.rebuild_day()
        self.focus()

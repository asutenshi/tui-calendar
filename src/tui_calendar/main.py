from datetime import date
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ContentSwitcher
from tui_calendar.ui.components.month_grid import MonthGrid
from tui_calendar.core.indexer import NotesIndexer


class WeekView(Static):
    def compose(self) -> ComposeResult:
        yield Static("🗓️ Week View (Columns will be here)")

class DayView(Static):
    def compose(self) -> ComposeResult:
        yield Static("📝 Day View (To-Do list will be here)")


class TuiCalApp(App):
    """Основное приложение TUI Calendar."""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    ContentSwitcher {
        height: 1fr;
        align: center middle;
    }
    
    WeekView, DayView {
        width: 100%;
        height: 100%;
        content-align: center middle;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("m", "switch_view('month')", "Month"),
        ("w", "switch_view('week')", "Week"),
        ("d", "switch_view('day')", "Day"),
        ("c, n", "create_new", "Create_new")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        
        with ContentSwitcher(initial="month", id="view-switcher"):
            yield MonthGrid(id="month")  
            yield WeekView(id="week")   
            yield DayView(id="day")   
            
        yield Footer()

    def action_switch_view(self, view_id: str) -> None:
        """Переключает текущий вид в ContentSwitcher."""
        self.query_one("#view-switcher", ContentSwitcher).current = view_id

    def on_mount(self) -> None:
        current_file_path = Path(__file__).resolve()
        project_root = current_file_path.parent
        notes_path = project_root.parent.parent / "examples" / "created_notes"
        self.indexer = NotesIndexer(notes_path)
        self.selected_date = date.today()

    def action_create_new(self) -> None:
        """Логика нажатия 'c' или 'n'"""
        new_file = self.indexer.create_note(self.selected_date, title="Untitled")
        self.notify(f"Created: {new_file.name}", title="Success", severity="information")


def run():
    app = TuiCalApp()
    app.run()


if __name__ == "__main__":
    run()

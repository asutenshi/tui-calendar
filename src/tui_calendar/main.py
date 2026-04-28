from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ContentSwitcher
from tui_calendar.ui.components.month_grid import MonthGrid


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


def run():
    app = TuiCalApp()
    app.run()

if __name__ == "__main__":
    run()
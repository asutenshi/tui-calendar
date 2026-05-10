from datetime import date

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static, ContentSwitcher
from textual.reactive import reactive

from tui_calendar.ui.components.month_grid import MonthGrid


class WeekView(Static):
    def compose(self) -> ComposeResult:
        yield Static("🗓️ Week View (Columns will be here)")

class DayView(Static):
    def compose(self) -> ComposeResult:
        yield Static("📝 Day View (To-Do list will be here)")


class TuiCalApp(App):
    """Основное приложение TUI Calendar."""
    
    selected_date = reactive(date.today())

    TITLE = "TUI Calendar"
    MONTH_NAMES = [
        "", "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]

    CSS = """
    Screen {
        layout: vertical;
    }
    
    ContentSwitcher {
        height: 1fr;
    }
    
    MonthGrid, WeekView, DayView {
        width: 100%;
        height: 100%;
    }

    WeekView, DayView {
        content-align: center middle;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("m", "switch_view('month')", "Month"),
        Binding("w", "switch_view('week')", "Week"),
        Binding("d", "switch_view('day')", "Day"),
        Binding("t", "go_today", "Today"),  
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
        if view_id == "month":
            self.query_one("#month").focus()

    def watch_selected_date(self, old_val: date, new_val: date) -> None:
        """Автоматически обновляет подзаголовок при смене даты."""
        month_name = self.MONTH_NAMES[new_val.month]
        self.sub_title = f"{month_name} {new_val.year}"

    def action_go_today(self) -> None:
        """Возвращает календарь к сегодняшней дате."""
        self.selected_date = date.today()
        self.action_switch_view("month")
            
def run():
    app = TuiCalApp()
    app.run()

if __name__ == "__main__":
    run()
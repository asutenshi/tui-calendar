from datetime import date

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static, ContentSwitcher
from textual.reactive import reactive

from tui_calendar.ui.components.month_grid import MonthGrid
from tui_calendar.ui.components.week_view import WeekView
from tui_calendar.ui.components.day_view import DayView


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
        self.query_one(f"#{view_id}").focus()

    def watch_selected_date(self, old_val: date, new_val: date) -> None:
        """Автоматически обновляет подзаголовок при смене даты."""
        month_name = self.MONTH_NAMES[new_val.month]
        self.sub_title = f"{month_name} {new_val.year}"

    def action_go_today(self) -> None:
        """Возвращает календарь к сегодняшней дате в текущем активном виде."""
        self.selected_date = date.today()
        
        current_view = self.query_one("#view-switcher").current
        
        if current_view == "month":
            month_grid = self.query_one("#month")
            month_grid.current_year = self.selected_date.year
            month_grid.current_month = self.selected_date.month
            month_grid._update_focus()
        elif current_view == "week":
            self.query_one("#week").rebuild_week()
        elif current_view == "day":
            self.query_one("#day").rebuild_day()
            
def run():
    app = TuiCalApp()
    app.run()

if __name__ == "__main__":
    run()
from datetime import date
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import ContentSwitcher, Footer, Header

from tui_calendar.core.indexer import NotesIndexer
from tui_calendar.ui.components.day_view import DayView
from tui_calendar.ui.components.month_grid import MonthGrid
from tui_calendar.ui.components.week_view import WeekView


class TuiCalApp(App):
    """Основное приложение TUI Calendar."""

    selected_date = reactive(date.today())

    TITLE = "TUI Calendar"
    MONTH_NAMES = [
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
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
        Binding("escape", "exit_focus", "Exit Focus"),
        Binding("m", "switch_view('month')", "Month"),
        Binding("w", "switch_view('week')", "Week"),
        Binding("d", "switch_view('day')", "Day"),
        Binding("t", "go_today", "Today"),
        Binding("enter", "open_editor", "Open/Focus"), 
    ]

    def __init__(self):
        super().__init__() 
        notes_dir = Path("notes") 
        self.indexer = NotesIndexer(notes_dir) 

    selected_date = reactive(date.today())

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

    def action_exit_focus(self) -> None:
        """Выходит из режима фокуса внутри дня."""
        current_view = self.query_one("#view-switcher").current
        if current_view == "month":
            month_grid = self.query_one("#month")
            month_grid.is_day_focus_mode = False
            
            active_cell = month_grid.get_active_cell()
            if active_cell:
                active_cell.render_events()

    def action_open_editor(self) -> None:
        """Переходит в режим фокуса или открывает заметку в редакторе."""
        current_view = self.query_one("#view-switcher").current
        
        if current_view == "month":
            month_grid = self.query_one("#month")
            active_cell = month_grid.get_active_cell()

            if not active_cell or not active_cell.events:
                return

            if not month_grid.is_day_focus_mode:
                month_grid.is_day_focus_mode = True
                active_cell.render_events()
                return
            
            else:
                idx = active_cell.focused_idx
                file_path = active_cell.events[idx].path

                with self.suspend():
                    self.indexer.open_file_in_editor(file_path)

                month_grid.rebuild_grid()
                
        elif current_view == "week":
            self.query_one("#week").rebuild_week()
        elif current_view == "day":
            self.query_one("#day").rebuild_day()


def run():
    app = TuiCalApp()
    app.run()


if __name__ == "__main__":
    run()

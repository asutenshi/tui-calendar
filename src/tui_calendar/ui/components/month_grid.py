import calendar
from datetime import date, timedelta

from textual.app import ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Static

from tui_calendar.core.model import Event


class DayHeader(Static):
    """Заголовок дня недели."""

    pass


class DayCell(Static):
    """Ячейка дня с отрисовкой событий."""

    def __init__(self, day: int, events: list[Event] = None):
        super().__init__()
        self.day = day
        self.events = events or []

    def compose(self) -> ComposeResult:
        with Static(classes="inner-cell", expand=True) as container:
            if self.day != 0:
                yield Static(str(self.day), classes="day-number")
                
                visible_events = self.events[:2]
                for event in visible_events:
                    status_class = f"-{event.status}" if event.status else ""
                    yield Static(
                        event.title, 
                        classes=f"event-pill {status_class}"
                    )
                
                if len(self.events) > 2:
                    yield Static(f"+ {len(self.events) - 2} more...", classes="more-indicator")

class MonthGrid(Static):
    """Сетка месяца."""

    can_focus = True

    current_year = reactive(date.today().year)
    current_month = reactive(date.today().month)

    BINDINGS = [
        Binding("h", "move_left", "Left", show=False),
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("l", "move_right", "Right", show=False),
        Binding("ctrl+h", "prev_month", "Prev Month", show=False),
        Binding("backspace", "prev_month", "Prev Month", show=True),
        Binding("ctrl+l", "next_month", "Next Month", show=True),
    ]

    DEFAULT_CSS = """
    MonthGrid {
        layout: grid;
        grid-size: 7;
        grid-rows: 2 1fr 1fr 1fr 1fr 1fr 1fr;
        grid-columns: 1fr;
        grid-gutter: 0;
        width: 100%;
        height: 100%;
        border-top: solid $panel-lighten-3;  
        border-left: solid $panel-lighten-3;
    }
    
    DayHeader {
        content-align: center middle;
        height: 2;                  
        color: $text-muted;
        text-style: bold;
        border-right: solid $panel-lighten-3; 
        border-bottom: heavy $accent;
    }
    
    DayCell {
        border-right: solid $panel-lighten-3;
        border-bottom: solid $panel-lighten-3;
        padding: 0;
        margin: 0;
        width: 100%;
        height: 100%;
    }

    DayCell .inner-cell {
        width: 100%;
        height: 100%;
        padding: 0;
        layout: vertical;
        overflow-y: hidden;
    }
    
    .day-number {
        width: 100%;
        content-align: right top;
        color: $text-muted;
        padding-right: 1; 
        margin-bottom: 1; 
    }

    DayCell.-today .day-number {
        color: $success;
        text-style: bold;
    }

    .event-pill {
        width: 100%;
        height: 1;
        margin-bottom: 1; 
        padding: 0 1; 
        content-align: left middle;
        overflow-x: hidden;
    }

    .event-pill.-todo {
        border-left: solid $warning;
        background: $warning 15%;
        color: $text;
    }

    .event-pill.-in_progress {
        border-left: solid $accent;
        background: $accent 15%;
        color: $text;
    }

    .event-pill.-done {
        border-left: solid $success;
        background: $success 15%;
        color: $text-muted;
        text-style: dim;
    }

    .more-indicator {
        color: $text-muted;
        text-style: italic;
        margin-left: 1; 
    }

    DayCell.-empty .inner-cell {
        background: $background;
    }

    DayCell.-today .inner-cell {
        color: $success;
        text-style: bold;
    }
    
    DayCell.-active .inner-cell {
        background: $boost;
        color: $text;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day_name in days_of_week:
            yield DayHeader(day_name)

    def on_mount(self) -> None:
        self.day_cells = [] 
        self.current_year = self.app.selected_date.year
        self.current_month = self.app.selected_date.month
        self.rebuild_grid()

    def rebuild_grid(self) -> None:
        self.query(DayCell).remove()
        self.day_cells = [] 

        start_date = date(self.current_year, self.current_month, 1)
        end_date = start_date + timedelta(days=32) 
        all_month_events = self.app.indexer.get_event_for_range(start_date, end_date)

        today = date.today()
        cal = calendar.Calendar(firstweekday=0)
        
        for day in cal.itermonthdays(self.current_year, self.current_month):
            day_events = [e for e in all_month_events if e.date.day == day] if day != 0 else []
            
            cell = DayCell(day=day, events=day_events)
            
            if day == 0:
                cell.add_class("-empty")
            elif (day == today.day and 
                  self.current_month == today.month and 
                  self.current_year == today.year):
                cell.add_class("-today")
                
            self.day_cells.append(cell)

        self.mount(*self.day_cells) 
        self._update_focus() 

    def watch_current_month(self, old_val: int, new_val: int) -> None:
        if old_val != new_val:
            self.rebuild_grid()

    def watch_current_year(self, old_val: int, new_val: int) -> None:
        if old_val != new_val:
            self.rebuild_grid()

    def _update_focus(self) -> None:
        """Синхронизирует фокус на сетке с self.app.selected_date"""
        selected = self.app.selected_date
        for cell in self.day_cells:
            if cell.day == 0:
                continue
            if (
                cell.day == selected.day
                and self.current_month == selected.month
                and self.current_year == selected.year
            ):
                cell.add_class("-active")
            else:
                cell.remove_class("-active")

    def _change_date(self, delta_days: int) -> None:
        """Умное перемещение с помощью timedelta. Никаких границ индексов!"""
        new_date = self.app.selected_date + timedelta(days=delta_days)
        self.app.selected_date = new_date

        if new_date.month != self.current_month or new_date.year != self.current_year:
            self.current_year = new_date.year
            self.current_month = new_date.month
        else:
            self._update_focus()

    def action_move_left(self) -> None:
        self._change_date(-1)

    def action_move_right(self) -> None:
        self._change_date(1)

    def action_move_up(self) -> None:
        self._change_date(-7)

    def action_move_down(self) -> None:
        self._change_date(7)

    def action_prev_month(self) -> None:
        y, m = self.current_year, self.current_month
        m -= 1
        if m == 0:
            m, y = 12, y - 1

        d = min(self.app.selected_date.day, calendar.monthrange(y, m)[1])
        self.app.selected_date = date(y, m, d)
        self.current_year, self.current_month = y, m

    def action_next_month(self) -> None:
        y, m = self.current_year, self.current_month
        m += 1
        if m == 13:
            m, y = 1, y + 1

        d = min(self.app.selected_date.day, calendar.monthrange(y, m)[1])
        self.app.selected_date = date(y, m, d)
        self.current_year, self.current_month = y, m

    def on_show(self) -> None:
        """Срабатывает каждый раз, когда мы возвращаемся с видов Week/Day на Month"""
        self.current_year = self.app.selected_date.year
        self.current_month = self.app.selected_date.month
        self._update_focus()
        self.focus()

import calendar
from datetime import date, timedelta

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static
from textual.reactive import reactive


class DayHeader(Static):
    """Заголовок дня недели."""

    pass


class DayCell(Static):
    """Ячейка дня."""

    def __init__(self, day: int):
        super().__init__()
        self.day = day

    def compose(self) -> ComposeResult:
        content = "" if self.day == 0 else f"{self.day}\n[mock event]"
        yield Static(content, classes="inner-cell", expand=True)


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
        /* Убираем все отступы у внешней ячейки, она только держит рамки */
        padding: 0; 
        margin: 0;
        width: 100%;
        height: 100%;
    }

    DayCell .inner-cell {
        width: 100%;
        height: 100%;
        padding: 0 1; /* Отступы для текста перенесли сюда */
    }

    DayCell.-empty .inner-cell {
        background: $background;
    }

    DayCell.-today .inner-cell {
        color: $success;
        text-style: bold;
    }
    
    /* Красим ТОЛЬКО внутренний блок, теперь он не подтечет под рамки */
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
        for cell in self.query(DayCell):
            cell.remove()

        today = date.today()
        cal = calendar.Calendar(firstweekday=0)
        self.day_cells = []

        for day in cal.itermonthdays(self.current_year, self.current_month):
            cell = DayCell(day=day)
            if day == 0:
                cell.add_class("-empty")
            elif (
                day == today.day
                and self.current_month == today.month
                and self.current_year == today.year
            ):
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

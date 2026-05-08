import calendar
from datetime import date

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
        content = "" if day == 0 else f"{day}\n[mock event]"
        super().__init__(content)
        self.day = day

def on_show(self) -> None:
        """Возвращает фокус сетке, когда вид становится активным."""
        self.focus()

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
        /* Указываем высоту строк: 2 для шапки, и шесть раз по 1fr для недель */
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
        height: 2;                  /* Уменьшили высоту шапки */
        color: $text-muted;
        text-style: bold;
        border-right: solid $panel-lighten-3; 
        border-bottom: heavy $accent;
    }
    
    DayCell {
        border-right: solid $panel-lighten-3; 
        border-bottom: solid $panel-lighten-3;
        content-align: left top;  
        padding: 1;
        height: 100%;
    }
    
    DayCell.-empty {
        /* Пустые дни */
    }

    DayCell.-today {
        color: $success;
        text-style: bold;
    }
    
    DayCell.-active {
        background: $accent;
        color: $background;
        text-style: bold;
        border-right: solid $panel-lighten-3; /* Заменили цвет */
        border-bottom: solid $panel-lighten-3;/* Заменили цвет */
    }
    """


    def compose(self) -> ComposeResult:
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for day_name in days_of_week:
            yield DayHeader(day_name)

    def on_mount(self) -> None:
        self.day_cells = []
        self.current_index = 0
        self.rebuild_grid() 

    def rebuild_grid(self) -> None:
        """Удаляет старые ячейки и рисует новый месяц."""
        for cell in self.query(DayCell):
            cell.remove()

        today = date.today()
        cal = calendar.Calendar(firstweekday=0)
        self.day_cells = []

        for day in cal.itermonthdays(self.current_year, self.current_month):
            cell = DayCell(day=day)
            if day == 0:
                cell.add_class("-empty")
            elif day == today.day and self.current_month == today.month and self.current_year == today.year:
                cell.add_class("-today")
            self.day_cells.append(cell)

        self.mount(*self.day_cells)

        self.current_index = 0
        for i, cell in enumerate(self.day_cells):
            if cell.day != 0:
                self.current_index = i
                break
        self._update_focus()

    def watch_current_month(self, old_val: int, new_val: int) -> None:
        if old_val != new_val:
            self.rebuild_grid()

    def watch_current_year(self, old_val: int, new_val: int) -> None:
        if old_val != new_val:
            self.rebuild_grid()

    def action_prev_month(self) -> None:
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1

    def action_next_month(self) -> None:
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

    def _update_focus(self) -> None:
        for i, cell in enumerate(self.day_cells):
            if i == self.current_index:
                cell.add_class("-active")
            else:
                cell.remove_class("-active")

    def _move(self, delta: int) -> None:
        new_index = self.current_index + delta
        if 0 <= new_index < len(self.day_cells) and self.day_cells[new_index].day != 0:
            self.current_index = new_index
            self._update_focus()

    def action_move_left(self) -> None:
        self._move(-1)

    def action_move_right(self) -> None:
        self._move(1)

    def action_move_up(self) -> None:
        self._move(-7)

    def action_move_down(self) -> None:
        self._move(7)



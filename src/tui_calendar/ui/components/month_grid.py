import calendar
from datetime import date

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static


class DayHeader(Static):
    """Заголовок дня недели."""
    pass


class DayCell(Static):
    """Ячейка дня."""
    def __init__(self, day: int):
        content = "" if day == 0 else f"{day}\n[mock event]"
        super().__init__(content)
        self.day = day


class MonthGrid(Static):
    """Сетка месяца."""
    
    can_focus = True

    BINDINGS = [
        Binding("h", "move_left", "Left", show=False),
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("l", "move_right", "Right", show=False),
    ]

    DEFAULT_CSS = """
    MonthGrid {
        layout: grid;
        grid-size: 7;
        grid-columns: 1fr;
        grid-gutter: 0;
        width: 100%;
        height: 100%;
        border-top: solid $surface;
        border-left: solid $surface;
    }
    
    DayHeader {
        content-align: center middle;
        height: 3;
        color: $text-muted;
        text-style: bold;
        border-right: solid $surface;
        border-bottom: heavy $accent;
    }
    
    DayCell {
        border-right: solid $surface;
        border-bottom: solid $surface;
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
        border-right: solid $surface;
        border-bottom: solid $surface;
    }
    """

    def compose(self) -> ComposeResult:
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for day_name in days_of_week:
            yield DayHeader(day_name)

        today = date.today()
        cal = calendar.Calendar(firstweekday=0)
        
        for day in cal.itermonthdays(today.year, today.month):
            cell = DayCell(day=day)
            if day == 0:
                cell.add_class("-empty")
            elif day == today.day:
                cell.add_class("-today") 
            yield cell

    def on_mount(self) -> None:
        self.day_cells = list(self.query(DayCell))
        self.current_index = 0
        
        for i, cell in enumerate(self.day_cells):
            if cell.day != 0:
                self.current_index = i
                break
                
        self._update_focus()
        self.focus() 

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
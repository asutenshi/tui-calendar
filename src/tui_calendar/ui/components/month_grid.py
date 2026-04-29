import calendar
from datetime import date
from textual.app import ComposeResult
from textual.widgets import Static
from textual.binding import Binding

class DayCell(Static):
    """Виджет отдельной ячейки дня."""
    
    def __init__(self, day: int, is_current_month: bool):
        super().__init__()
        self.day = day
        self.is_current_month = is_current_month

    def render(self) -> str:
        if self.day == 0 or not self.is_current_month:
            return ""
        return f"{self.day}\n[mock event]"


class MonthGrid(Static):
    """Сетка месяца."""
    
    can_focus = True

    BINDINGS = [
        Binding("h", "move_left", "Left", show=False),
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("l", "move_right", "Right", show=False),
    ]

    CSS = """
    MonthGrid {
        layout: grid;
        grid-size: 7;
        grid-columns: 1fr;
        grid-rows: 1fr;
        grid-gutter: 1 2;
        padding: 1;
    }
    
    DayCell {
        border: solid $surface;
        content-align: center middle;
        height: 100%;
    }
    
    DayCell.-active {
        border: double $accent;
        background: $boost;
    }
    """

    def compose(self) -> ComposeResult:
        today = date.today()
        cal = calendar.Calendar(firstweekday=0)
        
        for day in cal.itermonthdays(today.year, today.month):
            yield DayCell(day=day, is_current_month=(day != 0))

    def on_mount(self) -> None:
        """Срабатывает после построения интерфейса."""
        self.cells = list(self.query(DayCell))
        self.current_index = 0
        
        for i, cell in enumerate(self.cells):
            if cell.day != 0:
                self.current_index = i
                break
                
        self._update_focus()
        self.focus() 

    def _update_focus(self) -> None:
        """Обновляет классы для подсветки активной ячейки."""
        for i, cell in enumerate(self.cells):
            if i == self.current_index:
                cell.add_class("-active")
            else:
                cell.remove_class("-active")

    def _move(self, delta: int) -> None:
        """Вспомогательная функция для перемещения фокуса."""
        new_index = self.current_index + delta
        
        if 0 <= new_index < len(self.cells):
            if self.cells[new_index].day != 0:
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
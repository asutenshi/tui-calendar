import calendar
from datetime import date
from textual.app import ComposeResult
from textual.widgets import Static

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
    
    CSS = """
    MonthGrid {
        layout: grid;
        grid-size: 7; /* 7 колонок для дней недели */
        grid-columns: 1fr;
        grid-rows: 1fr;
        grid-gutter: 1 2; /* отступы между ячейками */
        padding: 1;
    }
    
    DayCell {
        border: solid $surface;
        content-align: center middle;
        height: 100%;
    }
    
    /* Этот класс мы будем добавлять через Python для подсветки фокуса */
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
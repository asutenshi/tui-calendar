from datetime import date, timedelta

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static

class DayColumn(Static):
    """Колонка одного дня в неделе."""
    def __init__(self, current_date: date):
        # Форматируем заголовок: например, "Mon 25"
        header = current_date.strftime("%a %d")
        super().__init__(f"{header}\n\n[mock tasks]")
        self.date = current_date

class WeekView(Static):
    """Отображение недели (7 колонок)."""
    
    can_focus = True

    BINDINGS = [
        Binding("h", "move_left", "Left", show=False),
        Binding("l", "move_right", "Right", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("j", "move_down", "Down", show=False),
    ]

    DEFAULT_CSS = """
    WeekView {
        layout: grid;
        grid-size: 7 1; /* 7 колонок, 1 строка */
        width: 100%;
        height: 100%;
        border-top: solid $panel-lighten-3;  
        border-left: solid $panel-lighten-3; 
    }

    DayColumn {
        border-right: solid $panel-lighten-3;
        border-bottom: solid $panel-lighten-3;
        content-align: center top;
        padding: 1;
        height: 100%;
    }

    DayColumn.-active {
        background: $boost;
    }
    """

    def compose(self) -> ComposeResult:
        # При создании виджета отдаем 7 пустых колонок, они заполнятся в on_mount
        for _ in range(7):
            yield DayColumn(date.today())

    def on_mount(self) -> None:
        self.rebuild_week()

    def rebuild_week(self) -> None:
        selected = self.app.selected_date
        start_of_week = selected - timedelta(days=selected.weekday())
        
        columns = self.query(DayColumn)
        if not columns:
            return
            
        for i, col in enumerate(columns):
            current_day = start_of_week + timedelta(days=i)
            col.date = current_day
            
            header = current_day.strftime("%a %d")
            col.update(f"{header}\n\n[mock tasks]")
            
            if current_day == selected:
                col.add_class("-active")
            else:
                col.remove_class("-active")

    def _change_date(self, delta_days: int) -> None:
        """Меняет глобальную дату и перерисовывает неделю."""
        self.app.selected_date += timedelta(days=delta_days)
        self.rebuild_week()

    def action_move_left(self) -> None:
        self._change_date(-1)

    def action_move_right(self) -> None:
        self._change_date(1)

    def action_move_up(self) -> None:
        self._change_date(-7)

    def action_move_down(self) -> None:
        self._change_date(7)
        
    def on_show(self) -> None:
        """При переключении на этот вид обновляем данные и забираем фокус."""
        self.rebuild_week()
        self.focus()
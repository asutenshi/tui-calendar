from datetime import date, timedelta

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static


class DayColumn(Static):
    """Колонка одного дня в неделе."""
    def __init__(self, day_date: date):
        super().__init__()
        self.date = day_date

    def compose(self) -> ComposeResult:
        header = self.date.strftime("%a %d")
        yield Static(f"{header}\n\n[mock tasks]", classes="inner-cell", expand=True)


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
        padding: 0;
        margin: 0;
        width: 1fr;
        height: 100%;
    }

    DayColumn .inner-cell {
        width: 100%;
        height: 100%;
        padding: 0 1;
    }

    DayColumn.-active .inner-cell {
        background: $boost;
        color: $text;
        text-style: bold;
    }
    """

    def on_mount(self) -> None:
        self._rendered_monday = None  
        self.rebuild_week()

    def _get_monday(self, d: date) -> date:
        return d - timedelta(days=d.weekday())

    def rebuild_week(self) -> None:
        selected = self.app.selected_date
        target_monday = self._get_monday(selected)
        
        if self._rendered_monday == target_monday:
            self._update_focus()
            return
            
        self.query(DayColumn).remove()
        self._rendered_monday = target_monday
        
        columns = []
        for i in range(7):
            current_date = target_monday + timedelta(days=i)
            col = DayColumn(current_date)
            if current_date == selected:
                col.add_class("-active")
            columns.append(col)
            
        self.mount(*columns)

    def _update_focus(self) -> None:
        selected = self.app.selected_date
        for col in self.query(DayColumn):
            if col.date == selected:
                col.add_class("-active")
            else:
                col.remove_class("-active")

    def _change_date(self, delta_days: int) -> None:
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
        """Срабатывает при возврате в вид недели."""
        self.rebuild_week()
        self.focus()
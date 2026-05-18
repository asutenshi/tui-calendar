import calendar
from datetime import date, timedelta

from textual.app import ComposeResult
from textual.binding import Binding
from textual.events import Resize
from textual.reactive import reactive
from textual.widgets import Static

from tui_calendar.core.model import Event
from tui_calendar.ui.screens.dialogs import DeleteConfirmDialog


class DayHeader(Static):
    """Заголовок дня недели."""

    pass


class DayCell(Static):
    """Ячейка дня с отрисовкой событий и поддержкой скролла."""

    def __init__(self, cell_date: date | None, events: list[Event] = None, **kwargs):
        super().__init__(**kwargs)
        self.cell_date = cell_date
        self.day = cell_date.day if cell_date else 0
        self.events = events or []
        self.focused_idx = 0
        self.note_offset = 0
        self.max_visible = 1

    def compose(self) -> ComposeResult:
        with Static(classes="inner-cell"):
            if self.day != 0:
                with Static(classes="cell-header"):
                    yield Static("", classes="cell-counter")
                    yield Static(str(self.day), classes="day-number")

    def on_mount(self) -> None:
        self.render_events()

    def render_events(self) -> None:
        container = self.query_one(".inner-cell")

        for widget in container.query(".event-pill"):
            widget.remove()

        if self.day == 0:
            return

        if not self.events:
            self.query_one(".cell-counter").update("")
            return

        month_grid = self.app.query_one("#month")
        is_mode_active = month_grid.is_day_focus_mode and self.has_class("-active")

        counter_label = self.query_one(".cell-counter")
        total = len(self.events)

        if is_mode_active and total > 0:
            counter_label.update(f"[{self.focused_idx + 1}/{total}]")
        elif total > 0:
            counter_label.update(f"[0/{total}]")

        else:
            counter_label.update("")

        visible = self.events[self.note_offset : self.note_offset + self.max_visible]

        for i, event in enumerate(visible):
            actual_idx = self.note_offset + i
            status_class = f"-{event.status}" if event.status else ""
            focus_class = "-focused" if (actual_idx == self.focused_idx and is_mode_active) else ""

            pill = Static(event.title, classes=f"event-pill {status_class} {focus_class}")
            container.mount(pill)

    def on_resize(self, event: Resize) -> None:
        """Пересчитываем количество видимых заметок при ресайзе терминала."""
        new_max = max(1, self.content_size.height - 1)

        if new_max != self.max_visible:
            self.max_visible = new_max

            if self.note_offset > 0 and self.note_offset + self.max_visible > len(self.events):
                self.note_offset = max(0, len(self.events) - self.max_visible)

            self.render_events()

    def move_focus(self, delta: int) -> None:
        if not self.events:
            return

        total = len(self.events)

        self.focused_idx = (self.focused_idx + delta) % total

        if self.focused_idx < self.note_offset:
            self.note_offset = self.focused_idx
        elif self.focused_idx >= self.note_offset + self.max_visible:
            self.note_offset = self.focused_idx - self.max_visible + 1

        try:
            month_grid = self.app.query_one("#month")
            month_grid.cell_states[self.cell_date] = {
                "focused_idx": self.focused_idx,
                "note_offset": self.note_offset,
            }
        except Exception:
            pass

        self.render_events()


class MonthGrid(Static):
    """Сетка месяца."""

    can_focus = True
    current_year = reactive(date.today().year)
    current_month = reactive(date.today().month)

    is_day_focus_mode = reactive(False)

    BINDINGS = [
        # Навигация по сетке
        Binding("h", "move_left", "Left", show=False),
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("l", "move_right", "Right", show=False),
        # Взаимодействие с ячейкой
        Binding("enter", "open_editor", "Enter Day", show=False),
        Binding("escape", "exit_focus", "Exit Day", show=False),
        # Удаление
        Binding("d", "delete_note", "Delete Note", show=False),
        # Переключение месяцев
        Binding("ctrl+h", "prev_month", "Prev Month", show=False),
        Binding("backspace", "prev_month", "Prev Month", show=True),
        Binding("ctrl+l", "next_month", "Next Month", show=True),
        # Перемещение заметок
        Binding("H", "move_note('left')", "Move 1 day back", show=False),
        Binding("J", "move_note('down')", "Move 1 week forward", show=False),
        Binding("K", "move_note('up')", "Move 1 week back", show=False),
        Binding("L", "move_note('right')", "Move 1 day forward", show=False),
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
        margin: 0;
        layout: vertical;
        overflow-y: hidden;
    }
    
    .cell-header {
        width: 100%;
        height: 1;
        layout: horizontal;
    }

    .cell-counter {
        width: 1fr;
        content-align: left top;
        color: $text-muted;
        padding-left: 1;
        text-style: bold;
    }

    .day-number {
        width: 1fr;
        content-align: right top;
        color: $text-muted;
        padding-right: 1; 
    }

    DayCell.-today .day-number {
        color: $success;
        text-style: bold;
    }

    DayCell.-active {
        outline: none;
    }
    
    DayCell.-active .inner-cell {
        background: rgba(150, 150, 150, 0.2); 
    }

    MonthGrid.-editing-mode DayCell.-active .cell-counter,
    MonthGrid.-editing-mode DayCell.-active .day-number {
        color: $success; 
        text-style: bold;
    }


    .event-pill {
        width: 100%;
        height: 1;
        margin: 0;
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
        color: $text;

    }

    /* СТИЛИ ФОКУСА ЗАМЕТОК */
    .event-pill.-focused {
        background: $primary; 
        color: $background;
        text-style: bold;
    }

    .event-pill.-todo.-focused {
        background: $warning;
        color: $background;
        text-style: bold;
    }

    .event-pill.-in_progress.-focused {
        background: $accent;
        color: $background;
        text-style: bold;
    }

    .event-pill.-done.-focused {
        background: $success;
        color: $background;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day_name in days_of_week:
            yield DayHeader(day_name)

    def on_mount(self) -> None:
        self.cell_states: dict[date, dict] = {}

        self.day_cells = []
        self.current_year = self.app.selected_date.year
        self.current_month = self.app.selected_date.month
        self.rebuild_grid()

    def watch_is_day_focus_mode(self, old_val: bool, new_val: bool) -> None:
        """Срабатывает автоматически при изменении флажка режима."""
        if new_val:
            self.add_class("-editing-mode")
        else:
            self.remove_class("-editing-mode")

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

            cell_date = date(self.current_year, self.current_month, day) if day != 0 else None

            cell = DayCell(cell_date=cell_date, events=day_events)

            if cell_date and cell_date in getattr(self, "cell_states", {}):
                state = self.cell_states[cell_date]

                max_idx = max(0, len(day_events) - 1)
                cell.focused_idx = min(state["focused_idx"], max_idx)

                max_offset = max(0, len(day_events) - cell.max_visible)
                cell.note_offset = min(state["note_offset"], max_offset)

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

    def get_active_cell(self) -> DayCell | None:
        """Вспомогательный метод для получения текущей выделенной ячейки."""
        selected = self.app.selected_date
        for cell in self.day_cells:
            if cell.day == selected.day:
                return cell
        return None

    def action_move_left(self) -> None:
        if not self.is_day_focus_mode:
            self._change_date(-1)

    def action_move_right(self) -> None:
        if not self.is_day_focus_mode:
            self._change_date(1)

    def action_move_up(self) -> None:
        if self.is_day_focus_mode:
            active = self.get_active_cell()
            if active:
                active.move_focus(-1)
        else:
            self._change_date(-7)

    def action_move_down(self) -> None:
        if self.is_day_focus_mode:
            active = self.get_active_cell()
            if active:
                active.move_focus(1)
        else:
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

    def action_delete_note(self) -> None:
        """Handles 'd' key press to delete the focused note."""
        active_cell = self.get_active_cell()

        if not self.is_day_focus_mode or not active_cell or not active_cell.events:
            return

        event_to_delete = active_cell.events[active_cell.focused_idx]

        def check_deletion(result: bool) -> None:
            if result:
                self.app.indexer.delete_note(event_to_delete.path)

                self.rebuild_grid()

                if not self.get_active_cell().events:
                    self.is_day_focus_mode = False

                self.app.notify(f"Note '{event_to_delete.title}' deleted successfully")

        self.app.push_screen(DeleteConfirmDialog(event_to_delete.title), check_deletion)

    def action_move_note(self, direction: str) -> None:
        if not getattr(self, "is_day_focus_mode", False):
            return

        active_cell = self.get_active_cell()
        if not active_cell or not active_cell.events:
            return

        current_idx = active_cell.focused_idx
        event_to_move = active_cell.events[current_idx]
        current_date = event_to_move.date

        if direction == "left":
            delta = timedelta(days=-1)
        elif direction == "right":
            delta = timedelta(days=1)
        elif direction == "up":
            delta = timedelta(days=-7)
        elif direction == "down":
            delta = timedelta(days=7)
        else:
            return

        new_date = current_date + delta

        try:
            event_to_move.date = new_date
            self.app.indexer.update_note(event_to_move)

            old_path = event_to_move.path
            old_date_str = str(current_date)
            new_date_str = str(new_date)

            if old_path.name.startswith(old_date_str):
                new_name = old_path.name.replace(old_date_str, new_date_str, 1)
                new_path = old_path.with_name(new_name)

                counter = 1
                base_new_path = new_path
                while new_path.exists():
                    new_path = base_new_path.with_stem(f"{base_new_path.stem}_{counter}")
                    counter += 1

                old_path.rename(new_path)
                event_to_move.path = new_path

        except Exception as e:
            self.app.notify(f"Move error: {e}", severity="error")
            return

        if new_date.year != self.current_year or new_date.month != self.current_month:
            self.app.selected_date = new_date
            self.current_year = new_date.year
            self.current_month = new_date.month
            self.set_timer(0.1, lambda: self._restore_note_focus(event_to_move.title))
            return

        dest_cell = None
        for cell in self.day_cells:
            if cell.cell_date == new_date:
                dest_cell = cell
                break

        if dest_cell:
            active_cell.events.pop(current_idx)

            if active_cell.events:
                active_cell.focused_idx = max(0, len(active_cell.events) - 1)
                active_cell.note_offset = max(
                    0, active_cell.focused_idx - active_cell.max_visible + 1
                )
            else:
                active_cell.focused_idx = 0
                active_cell.note_offset = 0

            self.cell_states[active_cell.cell_date] = {
                "focused_idx": active_cell.focused_idx,
                "note_offset": active_cell.note_offset,
            }

            try:
                active_cell.render_events()
            except Exception:
                pass

            dest_cell.events.append(event_to_move)
            self.app.selected_date = new_date
            self._update_focus()
            self.is_day_focus_mode = True
            self.app.call_later(self._restore_note_focus, event_to_move.title)

    def _restore_note_focus(self, target_title: str) -> None:
        """Ищет перенесенную заметку в новой ячейке и выделяет её."""
        active_cell = self.get_active_cell()
        if not active_cell or not active_cell.events:
            return

        for idx, event in enumerate(active_cell.events):
            if event.title == target_title:
                active_cell.focused_idx = idx

                if idx >= active_cell.max_visible:
                    active_cell.note_offset = idx - active_cell.max_visible + 1
                else:
                    active_cell.note_offset = 0

                self.cell_states[active_cell.cell_date] = {
                    "focused_idx": active_cell.focused_idx,
                    "note_offset": active_cell.note_offset,
                }

                self.is_day_focus_mode = True

                try:
                    active_cell.render_events()
                except Exception:
                    pass
                break

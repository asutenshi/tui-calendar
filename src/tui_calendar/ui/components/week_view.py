from datetime import date, timedelta

from textual.app import ComposeResult
from textual.binding import Binding
from textual.events import Resize
from textual.reactive import reactive
from textual.widgets import Static
from textual.color import Color

from tui_calendar.core.model import Event
from tui_calendar.ui.screens.dialogs import DeleteConfirmDialog


class DayColumn(Static):
    """Колонка одного дня в неделе с поддержкой заметок и фокуса."""

    def __init__(self, day_date: date, events: list[Event] = None, **kwargs):
        super().__init__(**kwargs)
        self.date = day_date
        self.events = events or []
        self.focused_idx = 0
        self.note_offset = 0
        self.max_visible = 1

    def compose(self) -> ComposeResult:
        header_name = self.date.strftime("%a")
        header_num = self.date.strftime("%d")
        
        with Static(classes="cell-header"):
            yield Static("", classes="cell-counter")
            yield Static(f"{header_name} {header_num}", classes="day-number")
            
        yield Static(classes="inner-cell")

    def on_mount(self) -> None:
        self.render_events()

    def render_events(self) -> None:
        container = self.query_one(".inner-cell")

        for widget in container.query(".event-pill"):
            widget.remove()

        if not self.events:
            self.query_one(".cell-counter").update("")
            return

        week_grid = self.app.query_one("#week")
        is_mode_active = week_grid.is_day_focus_mode and self.has_class("-active")

        counter_label = self.query_one(".cell-counter")
        total = len(self.events)

        if is_mode_active and total > 0:
            counter_label.update(f"[{self.focused_idx + 1}/{total}]")
        elif total > 0:
            counter_label.update(f"[0/{total}]")
        else:
            counter_label.update("")

        visible = self.events[self.note_offset : self.note_offset + self.max_visible]

        try:
            tag_colors = self.app.config_manager.get_tag_color()
        except AttributeError:
            tag_colors = {}

        DEFAULT_HEX_COLOR = "#5c6370"

        for i, event in enumerate(visible):
            actual_idx = self.note_offset + i
            status_class = f"-{event.status}" if event.status else ""
            focus_class = "-focused" if (actual_idx == self.focused_idx and is_mode_active) else ""

            pill = Static(event.title, classes=f"event-pill {status_class} {focus_class}")
            
            if not focus_class:
                hex_color = self._get_event_color(event, tag_colors)
                if not hex_color:
                    hex_color = DEFAULT_HEX_COLOR
                    
                try:
                    base_color = Color.parse(hex_color)
                    pill.styles.background = base_color.with_alpha(0.15) 
                    pill.styles.border_left = ("solid", base_color)      
                except Exception:
                    pass

            container.mount(pill)

    def on_resize(self, event: Resize) -> None:
        new_max = max(1, self.content_size.height - 2) # Учитываем высоту заголовка
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
            week_grid = self.app.query_one("#week")
            week_grid.cell_states[self.date] = {
                "focused_idx": self.focused_idx,
                "note_offset": self.note_offset,
            }
        except Exception:
            pass

        self.render_events()

    def _get_event_color(self, event: Event, tag_colors: dict[str, str]) -> str | None:
        if not event.tags:
            return None
        for tag in event.tags:
            if tag in tag_colors:
                return tag_colors[tag] 
        return None


class WeekView(Static):
    """Отображение недели (7 колонок)."""

    can_focus = True
    is_day_focus_mode = reactive(False)

    BINDINGS = [
        Binding("h", "move_left", "Left", show=False),
        Binding("l", "move_right", "Right", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("j", "move_down", "Down", show=False),
        Binding("enter", "open_editor", "Enter Day", show=False),
        Binding("escape", "exit_focus", "Exit Day", show=False),
        Binding("d", "delete_note", "Delete Note", show=False),
        Binding("H", "move_note('left')", "Move 1 day back", show=False),
        Binding("J", "move_note('down')", "Move 1 week forward", show=False),
        Binding("K", "move_note('up')", "Move 1 week back", show=False),
        Binding("L", "move_note('right')", "Move 1 day forward", show=False),
        Binding("n", "create_note", "New Note", show=True),
    ]

    DEFAULT_CSS = """
    WeekView {
        layout: grid;
        grid-size: 7 1;
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
        padding: 0;
        margin: 0;
        layout: vertical;
        overflow-y: hidden;
    }

    .cell-header {
        width: 100%;
        height: 2;
        layout: horizontal;
        border-bottom: heavy $accent;
    }

    .cell-counter {
        width: 1fr;
        content-align: left middle;
        color: $text-muted;
        padding-left: 1;
        text-style: bold;
    }

    .day-number {
        width: 1fr;
        content-align: right middle;
        color: $text-muted;
        padding-right: 1; 
    }

    DayColumn.-today .day-number {
        color: $success;
        text-style: bold;
    }

    DayColumn.-active {
        outline: none;
    }

    DayColumn.-active .inner-cell {
        background: rgba(150, 150, 150, 0.2); 
    }

    WeekView.-editing-mode DayColumn.-active .cell-counter,
    WeekView.-editing-mode DayColumn.-active .day-number {
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

    .event-pill.-focused {
        background: $primary; 
        color: $background;
        text-style: bold;
    }
    """

    def on_mount(self) -> None:
        self.cell_states: dict[date, dict] = {}
        self.day_columns = []
        self._rendered_monday = None
        self.rebuild_week()

    def watch_is_day_focus_mode(self, old_val: bool, new_val: bool) -> None:
        if new_val:
            self.add_class("-editing-mode")
        else:
            self.remove_class("-editing-mode")

    def _get_monday(self, d: date) -> date:
        return d - timedelta(days=d.weekday())

    def rebuild_week(self) -> None:
        self.query(DayColumn).remove()
        self.day_columns = []
        
        selected = self.app.selected_date
        target_monday = self._get_monday(selected)
        self._rendered_monday = target_monday
        today = date.today()

        start_date = target_monday
        end_date = start_date + timedelta(days=6)
        all_week_events = self.app.indexer.get_event_for_range(start_date, end_date)

        for i in range(7):
            current_date = target_monday + timedelta(days=i)
            day_events = [e for e in all_week_events if e.date == current_date]

            col = DayColumn(day_date=current_date, events=day_events)

            if current_date in getattr(self, "cell_states", {}):
                state = self.cell_states[current_date]
                max_idx = max(0, len(day_events) - 1)
                col.focused_idx = min(state["focused_idx"], max_idx)
                max_offset = max(0, len(day_events) - col.max_visible)
                col.note_offset = min(state["note_offset"], max_offset)

            if current_date == today:
                col.add_class("-today")

            if current_date == selected:
                col.add_class("-active")
                
            self.day_columns.append(col)

        self.mount(*self.day_columns)

    def _update_focus(self) -> None:
        selected = self.app.selected_date
        for col in self.day_columns:
            if col.date == selected:
                col.add_class("-active")
            else:
                col.remove_class("-active")

    def _change_date(self, delta_days: int) -> None:
        new_date = self.app.selected_date + timedelta(days=delta_days)
        old_monday = self._get_monday(self.app.selected_date)
        new_monday = self._get_monday(new_date)
        
        self.app.selected_date = new_date

        if old_monday != new_monday:
            self.rebuild_week()
        else:
            self._update_focus()

    def get_active_cell(self) -> DayColumn | None:
        selected = self.app.selected_date
        for col in self.day_columns:
            if col.date == selected:
                return col
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

    def on_show(self) -> None:
        self.rebuild_week()
        self.focus()

    def action_delete_note(self) -> None:
        active_cell = self.get_active_cell()

        if not self.is_day_focus_mode or not active_cell or not active_cell.events:
            return

        event_to_delete = active_cell.events[active_cell.focused_idx]

        def check_deletion(result: bool) -> None:
            if result:
                self.app.indexer.delete_note(event_to_delete.path)
                self.rebuild_week()

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
            old_path = event_to_move.path
            raw_content = ""
            if old_path.exists():
                raw_content = old_path.read_text(encoding="utf-8")

            event_to_move.date = new_date

            old_date_str = str(current_date)
            new_date_str = str(new_date)
            new_path = old_path

            if old_path.name.startswith(old_date_str):
                new_name = old_path.name.replace(old_date_str, new_date_str, 1)
                new_path = old_path.with_name(new_name)

                counter = 1
                base_new_path = new_path
                while new_path.exists():
                    new_path = base_new_path.with_stem(f"{base_new_path.stem}_{counter}")
                    counter += 1

            new_path.write_text(raw_content, encoding="utf-8")
            event_to_move.path = new_path

            if old_path != new_path and old_path.exists():
                old_path.unlink()

            self.app.indexer.update_note(event_to_move)

        except Exception as e:
            self.app.notify(f"Move error: {e}", severity="error")
            return

        old_monday = self._get_monday(current_date)
        new_monday = self._get_monday(new_date)

        if old_monday != new_monday:
            self.app.selected_date = new_date
            self.rebuild_week()
            self.set_timer(0.1, lambda: self._restore_note_focus(event_to_move.title))
            return

        dest_cell = None
        for col in self.day_columns:
            if col.date == new_date:
                dest_cell = col
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

            self.cell_states[active_cell.date] = {
                "focused_idx": active_cell.focused_idx,
                "note_offset": active_cell.note_offset,
            }

            dest_cell.events.append(event_to_move)
            self.app.selected_date = new_date
            
            self._update_focus()
            self.is_day_focus_mode = True

            try:
                active_cell.render_events()
            except Exception:
                pass

            self.app.call_later(self._restore_note_focus, event_to_move.title)

    def _restore_note_focus(self, target_title: str) -> None:
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

                self.cell_states[active_cell.date] = {
                    "focused_idx": active_cell.focused_idx,
                    "note_offset": active_cell.note_offset,
                }

                self.is_day_focus_mode = True

                try:
                    active_cell.render_events()
                except Exception:
                    pass
                break
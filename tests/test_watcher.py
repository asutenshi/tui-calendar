import time
from pathlib import Path

from tui_calendar.core.watcher import NotesEventHandler


def test_handler_triggers_callback():
    """Проверяем, что хендлер вызывает колбэк при изменении файла."""

    calls = []

    def spy_callback(event_type: str, file_path: Path):
        calls.append((event_type, file_path))

    handler = NotesEventHandler(callback=spy_callback)

    class MockEvent:
        def __init__(self, src_path):
            self.src_path = src_path
            self.is_directory = False

    event = MockEvent("test_note.md")

    handler.on_created(event)

    time.sleep(0.6)

    assert len(calls) == 1
    assert calls[0][0] == "created"
    assert calls[0][1].name == "test_note.md"


def test_handler_ignores_non_md_files():
    """Проверяем, что файлы не .md игнорируются."""
    calls = []

    def spy_callback(event_type: str, file_path: Path):
        calls.append(event_type)

    handler = NotesEventHandler(callback=spy_callback)

    class MockEvent:
        def __init__(self, src_path):
            self.src_path = src_path
            self.is_directory = False

    event = MockEvent("image.png")

    handler.on_created(event)
    time.sleep(0.6)

    assert len(calls) == 0

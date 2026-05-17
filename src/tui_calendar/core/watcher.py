import threading
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class NotesEventHandler(FileSystemEventHandler):
    """Обработчик событий в файловой системе"""

    def __init__(self, callback: Callable[[str, Path], None]):
        self.callback = callback
        self._timers: dict[str, threading.Timer] = {}
        self.debounce_seconds = 0.5

    def _trigger_callback(self, event_type: str, file_path: Path):
        """Эта функция вызывается таймером, когда 'дребезг' закончился."""
        self.callback(event_type, file_path)

        path_str = str(file_path)
        if path_str in self._timers:
            del self._timers[path_str]

    def _handle_event(self, event_type: str, event: FileSystemEvent):
        """Общая логика фильтрации и настройки таймера."""
        if event.is_directory:
            return

        if not event.src_path.endswith(".md"):
            return

        file_path = Path(event.src_path)
        path_str = str(file_path)

        if path_str in self._timers:
            self._timers[path_str].cancel()

        timer = threading.Timer(
            self.debounce_seconds, self._trigger_callback, args=[event_type, file_path]
        )
        self._timers[path_str] = timer
        timer.start()

    def on_created(self, event: FileSystemEvent):
        self._handle_event("created", event)

    def on_modified(self, event: FileSystemEvent):
        self._handle_event("modified", event)

    def on_deleted(self, event: FileSystemEvent):
        self._handle_event("deleted", event)


class NotesWatcher:
    """
    Главный класс-менеджер. Отвечает за запуск и остановку фонового слежения.
    """

    def __init__(self, directory: str | Path, callback: Callable[[str, Path], None]):
        self.directory = str(Path(directory).expanduser().resolve())
        self.callback = callback
        self.observer: Observer | None = None

    def start(self):
        if self.Observer is not None:
            return

        event_handler = NotesEventHandler(self.callback)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()

    def stop(self):
        """Останавливает слежение (важно вызывать при закрытии приложения)."""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None

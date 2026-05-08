from datetime import date
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from .model import Event


class NotesIndexer:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory).expanduser().resolve()

    def get_events(self) -> list[Event]:
        events = []

        if not self.directory.exists():
            return []

        for file in self.directory.rglob("*.md"):
            if not file.is_file():
                continue

            try:
                post = frontmatter.load(file)

                if "date" not in post.metadata:
                    continue

                data = dict(post.metadata)
                data["path"] = file

                if not data.get("title"):
                    data["title"] = file.stem

                event_obj = Event(**data)
                events.append(event_obj)

            except (ValidationError, TypeError) as e:
                print(f"Ошибка валидации в файле {file.name}: {e}")
            except Exception as e:
                print(f"Не удалось прочитать файл {file.name}: {e}")

        return events

    def get_event_for_range(self, start_date: date, end_date: date) -> list[Event]:
        all_events = self.get_events()
        return [e for e in all_events if start_date <= e.date <= end_date]

from datetime import date
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from .model import Event


class NotesIndexer:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory).expanduser().resolve()
        self.directory.mkdir(parents=True, exist_ok=True)

    def get_note(self, file_path: Path):
        if not file_path.exists():
            return None

        try:
            post = frontmatter.load(file_path)

            if "date" not in post.metadata:
                return None

            data = dict(post.metadata)
            data["path"] = file_path

            if not data.get("title"):
                data["title"] = file_path.stem

            event_obj = Event(**data)

        except Exception as e:
            print(f"Ошибка при чтении файла {file_path.name}: {e}")
            return None

        return event_obj

    def update_note(self, event: Event):
        if not event.path.exists():
            return False

        try:
            post = frontmatter.load(event.path)
            post.metadata["date"] = event.date
            post.metadata["title"] = event.title
            post.metadata["status"] = event.status
            post.metadata["tags"] = event.tags

            with open(event.path, "wb") as file:
                frontmatter.dump(post, file)
            return True
        except Exception as e:
            print(f"Не удалось прочитать файл {event.path.name}: {e}")
            return False

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

    def create_note(
        self,
        target_date: date,
        title: str = "New Event",
        status: str | None = "todo",
        tags: list[str] | None = None,
    ) -> Path:
        if tags is None:
            tags = []
        safe_title = "".join([c if c.isalnum() else "-" for c in title.lower()]).strip("-")
        filename = f"{target_date}-{safe_title}.md"
        file_path = self.directory / filename

        counter = 1
        while file_path.exists():
            file_path = self.directory / f"{target_date}_{safe_title}_{counter}.md"
            counter += 1

        post = frontmatter.Post(
            content="# " + title, date=target_date, title=title, status=status, tags=tags
        )

        with open(file_path, "wb") as f:
            frontmatter.dump(post, f)

        return file_path

    def delete_note(self, file_path: Path) -> bool:
        """Удаляет файл заметки. Возвращает True при успехе, False если файла нет."""
        if not file_path.is_file():
            return False

        try:
            file_path.unlink()
            return True
        except Exception as e:
            # На случай, если нет прав доступа
            print(f"Ошибка при удалении {file_path}: {e}")
            return False

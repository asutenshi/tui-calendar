from pathlib import Path

import frontmatter
from pydantic import ValidationError

from .model import Event


class NotesIndexer:
    def __init__(self, directory: Path):
        self.directory = Path(directory)

    def get_events(self) -> list[Event]:
        events = []
        
        for file in self.directory.rglob("*.md"):
            if not file.is_file():
                continue
                
            try:
                post = frontmatter.load(file)
                
                event_data = post.metadata
                event_data['path'] = file
                
                event = Event(**event_data)
                events.append(event)
                
            except (ValidationError, TypeError) as e:
                print(f"Ошибка валидации в файле {file}: {e}")
            except Exception as e:
                print(f"Не удалось прочитать файл {file}: {e}")
                
        return events

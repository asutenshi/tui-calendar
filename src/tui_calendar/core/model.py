from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field


class Event(BaseModel):
    date: date
    title: str = "Untitled"
    status: str | None = "todo"
    tags: list[str] = Field(default_factory=list)
    path: Path

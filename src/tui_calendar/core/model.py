from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from pathlib import Path


class Event(BaseModel):
    date: date
    title: str = "Untitled"
    status: Optional[str] = "todo"
    tags: List[str] = Field(default_factory=list)
    path: Path

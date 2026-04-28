from datetime import date
from pathlib import Path

import pytest

from tui_calendar.core.indexer import NotesIndexer


@pytest.fixture
def temp_notes_dir(tmp_path):
    meeting_file = tmp_path / "2024-10-25-meeting.md"
    meeting_file.write_text(
        "---\ndate: 2024-10-25\ntitle: 'Встреча по MVP'\n---\nТекст", encoding="utf-8"
    )
    empty_title_file = tmp_path / "no-title-note.md"
    empty_title_file.write_text("---\ndate: 2024-10-30\n---\nТекст", encoding="utf-8")
    invalid_file = tmp_path / "invalid.md"
    invalid_file.write_text("---\ndate: 2023-13-45\ntitle: 'Ошибка'\n---\nТекст", encoding="utf-8")
    return tmp_path


def test_get_events_loading(temp_notes_dir):
    indexer = NotesIndexer(temp_notes_dir)
    events = indexer.get_events()
    assert len(events) == 2


def test_title_fallback_to_filename(temp_notes_dir):
    indexer = NotesIndexer(temp_notes_dir)
    events = indexer.get_events()
    note_30 = next(e for e in events if e.date == date(2024, 10, 30))
    assert note_30.title == "no-title-note"


def test_get_event_for_range(temp_notes_dir):
    indexer = NotesIndexer(temp_notes_dir)
    start = date(2024, 10, 1)
    end = date(2024, 10, 26)
    filtered = indexer.get_event_for_range(start, end)
    assert len(filtered) == 1


@pytest.fixture
def real_examples_dir():
    """Фикстура, которая находит папку examples в корне проекта"""
    path = Path(__file__).parent.parent / "examples"
    return path


def test_real_files_existence(real_examples_dir):
    """Проверяем, что папка с примерами вообще существует"""
    assert real_examples_dir.exists(), f"Папка {real_examples_dir} не найдена!"
    assert real_examples_dir.is_dir()


def test_real_files_parsing(real_examples_dir):
    """Проверяем, что индексатор видит файлы в папке examples"""
    indexer = NotesIndexer(real_examples_dir)
    events = indexer.get_events()

    assert len(events) >= 1

    titles = [e.title for e in events]
    assert any("Тренировка" in t for t in titles)

import os
from datetime import date
from unittest.mock import patch

import frontmatter
import pytest

from tui_calendar.core.indexer import NotesIndexer


@pytest.fixture
def indexer(tmp_path):
    """Создает индексатор, работающий во временной папке."""
    return NotesIndexer(tmp_path)


def test_create_note_file_exists(indexer):
    """Проверка, что файл физически создается."""
    target_date = date(2023, 11, 7)
    title = "Test Note"
    path = indexer.create_note(target_date, title)
    assert path.exists()
    assert path.is_file()


def test_create_note_yaml_content(indexer):
    """Проверка, что внутри файла правильный YAML заголовок."""
    target_date = date(2025, 1, 1)
    title = "New Year Party"
    path = indexer.create_note(target_date, title)
    post = frontmatter.load(path)
    assert post.metadata["title"] == "New Year Party"
    assert post.metadata["date"] == target_date
    assert post.metadata["status"] == "todo"
    assert post.metadata["tags"] == []
    assert post.content.strip() == "# New Year Party"


def test_create_note_custom_status_and_tags(indexer):
    """Проверка создания заметки с пользовательским статусом и тегами."""
    target_date = date(2023, 12, 31)
    title = "Buy gifts"
    custom_status = "in_progress"
    custom_tags = ["family", "finance", "urgent"]
    path = indexer.create_note(target_date, title, status=custom_status, tags=custom_tags)
    post = frontmatter.load(path)
    assert post.metadata["title"] == "Buy gifts"
    assert post.metadata["status"] == "in_progress"
    assert post.metadata["tags"] == ["family", "finance", "urgent"]


def test_create_note_slugification(indexer):
    """Проверка очистки имени файла от спецсимволов."""
    target_date = date(2023, 11, 7)
    title = "Hello World!!! @2023"
    path = indexer.create_note(target_date, title)
    assert " " not in path.name
    assert "@" not in path.name


def test_create_note_collision(indexer):
    """Проверка логики дубликатов (счетчик _1, _2)."""
    target_date = date(2023, 11, 7)
    title = "Meeting"
    path1 = indexer.create_note(target_date, title)
    path2 = indexer.create_note(target_date, title)
    path3 = indexer.create_note(target_date, title)
    assert path1.name == "2023-11-07-meeting.md"
    assert path2.name == "2023-11-07_meeting_1.md"
    assert path3.name == "2023-11-07_meeting_2.md"
    assert path1 != path2 != path3


def test_create_note_empty_title(indexer):
    """Проверка создания заметки без названия."""
    target_date = date(2023, 11, 7)
    path = indexer.create_note(target_date, title="Untitled")
    assert "untitled" in path.name
    post = frontmatter.load(path)
    assert post.metadata["title"] == "Untitled"


@patch("subprocess.run")
@patch("tui_calendar.core.indexer.NotesIndexer.get_events")
def test_open_file_in_editor(mock_get_events, mock_subprocess, indexer, tmp_path):
    test_file = tmp_path / "test.md"
    test_file.touch()

    with patch.dict(os.environ, {"EDITOR": "vim"}):
        indexer.open_file_in_editor(test_file)

    mock_subprocess.assert_called_once()

    args, kwargs = mock_subprocess.call_args
    assert args[0] == ["vim", str(test_file)]

    mock_get_events.assert_called_once()

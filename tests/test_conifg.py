from tui_calendar.core.config import ConfigManager


def test_config_generation(tmp_path):
    """Проверяет, что конфиг-файл автоматически создается при первой инициализации."""
    manager = ConfigManager(tmp_path)
    assert manager.config_path.exists()
    assert manager.config_path.name == "config.yaml"


def test_get_tag_colors_default(tmp_path):
    """Проверяет, что дефолтные цвета тегов корректно загружаются."""
    manager = ConfigManager(tmp_path)
    colors = manager.get_tag_color()
    assert isinstance(colors, dict)
    assert colors["work"] == "#E06C75"
    assert "urgent" in colors


def test_get_tag_colors_safe_read(tmp_path):
    """Проверяет защиту от сломанного/пустого конфига."""
    manager = ConfigManager(tmp_path)

    with open(manager.config_path, "w") as file:
        file.write("ui: \n  some_other_setting: true")

    colors = manager.get_tag_colors()

    assert colors == {}

from pathlib import Path

import yaml


class ConfigManager:
    """Менеджер конфигурации приложения"""

    def __init__(self, folder_path: Path):
        """
        Инициализирует менеджер и проверяет наличие файла конфигурации.

        Args:
            folder_path (Path): Путь к директории, где должен храниться конфиг.
        """
        self.config_path = folder_path / "config.yaml"
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        """
        Проверяет, существует ли конфигурационный файл.
        Если файла нет, генерирует его с настройками по умолчанию.
        """
        if self.config_path.exists():
            return False

        default_data = {
            "ui": {"tag_colors": {"work": "#E06C75", "personal": "#98C379", "urgent": "#E06C75"}}
        }
        with open(self.config_path, "w", encoding="utf-8") as file:
            yaml.dump(default_data, file, default_flow_style=False)

    def get_tag_color(self) -> dict:
        """
        Считывает конфигурационный файл и возвращает словарь с цветами тегов.
        Returns:
            dict: Словарь вида {'tag_name': 'hex_color'}.
            Если настройки повреждены или отсутствуют, возвращает пустой словарь {}.
        """
        with open(self.config_path, encoding="utf-8") as file:
            config = yaml.safe_load(file)
        if not config:
            return {}
        tag_colors = config.get("ui", {}).get("tag_colors", {})
        return tag_colors

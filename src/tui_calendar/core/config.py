import yaml
from pathlib import Path

class ConfigManager: 
    def __init__(self, folder_path: Path):
        self.config_path = folder_path / "config.yaml"
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if self.config_path.exists():
            return False

        default_data = {
            "ui": {
                "tag_colors":{
                    "work": "#E06C75",
                    "personal": "#98C379",
                    "urgent": "#E06C75"
                }
            }
        }
        with open(self.config_path, 'w', encoding="utf-8") as file:
          yaml.dump(default_data, file, default_flow_style=False)
      
    def get_tag_color(self):
        with open(self.config_path, 'r', encoding="utf-8") as file:
          config = yaml.safe_load(file)
        if not config:
           return {}
        tag_colors = config.get("ui", {}).get("tag_colors", {})
        return tag_colors

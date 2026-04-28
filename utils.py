import json
import os
from pathlib import Path

# Save settings to User profile directory: C:/Users/<User>/.lyricsfusion/settings.json
SETTINGS_DIR = Path.home() / ".lyricsfusion"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "db_path": "lyrics.db",
    "auto_save": False,
    "high_fidelity": True
}

class SettingsManager:
    @staticmethod
    def _ensure_dir():
        """Create the settings directory if it doesn't exist."""
        if not SETTINGS_DIR.exists():
            SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_settings():
        SettingsManager._ensure_dir()
        
        if not SETTINGS_FILE.exists():
            SettingsManager.save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS
        
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                # Ensure all default keys exist
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except Exception:
            return DEFAULT_SETTINGS

    @staticmethod
    def save_settings(settings):
        SettingsManager._ensure_dir()
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

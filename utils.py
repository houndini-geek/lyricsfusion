import json
import os
from pathlib import Path
import requests

# Save settings to User profile directory: C:/Users/<User>/.lyricsfusion/settings.json
SETTINGS_DIR = Path.home() / ".lyricsfusion"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"
SELLECTORS_FILE = SETTINGS_DIR / "selectors.json"

seletorsEndpoint = 'https://raw.githubusercontent.com/houndini-geek/lyricsfusion/refs/heads/master/selectors.json'
appVersionEndpoint = 'https://raw.githubusercontent.com/houndini-geek/lyricsfusion/refs/heads/master/current_app.json'

DEFAULT_SETTINGS = {
    "db_path": "lyrics.db",
    "auto_save": False,
    "high_fidelity": True
}

SELECTORS_SETTINGS = {
    "selectors":{
        "showmorebutton":{
        "selector":"full_width_button",
        "date":"04-29-2026",
        "last_modified": "04-29-2026",
        "date_format": "MM-DD-YY"
        },
        "searchresultpaginated":{
        "selector":"search-result-paginated-section",
        "date":"04-29-2026",
        "last_modified": "04-29-2026",
        "date_format": "MM-DD-YY"
        },
        "minisongcard":{
        "selector":"mini-song-card",
        "date":"04-29-2026",
        "last_modified": "04-29-2026",
        "date_format": "MM-DD-YY"
        },
        "minicardtitle":{
        "selector":"mini_card-title",
        "date":"04-29-2026",
        "last_modified": "04-29-2026",
        "date_format": "MM-DD-YY"
        },
        "minicardsubtitle":{
        "selector":"mini_card-subtitle",
        "date":"04-29-2026",
        "last_modified": "04-29-2026",
        "date_format": "MM-DD-YY"
        },
        "datalyricscontainer":{
        "selector":"[data-lyrics-container='true']",
        "date":"04-29-2026",
        "last_modified": "04-29-2026",
        "date_format": "MM-DD-YY"
        },
        "datalyricscontainerfallback":{
        "selector":"div[class*='Lyrics__Container']",
        "date":"04-29-2026",
        "last_modified": "04-29-2026",
        "date_format": "MM-DD-YY"
        }

       
    }
}








class SettingsManager:
    @staticmethod
    def _ensure_dir():
        """Create the settings directory if it doesn't exist."""
        if not SETTINGS_DIR.exists():
            SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def check_for_updates():
        try:
            response = requests.get(seletorsEndpoint)
            if response.status_code == 200:
                selectors = response.json()
                SettingsManager.save_selectors(selectors)
                return True
        except:
              return False
        
    @staticmethod
    def check_app_update()
        try:
            response = requests.get(seletorsEndpoint)
            if response.status_code == 200:
                selectors = response.json()
                SettingsManager.save_selectors(selectors)
                return True
        except:
              return False
    
        
    @staticmethod
    def load_selectors():
        SettingsManager._ensure_dir()

        if not SELLECTORS_FILE.exists():
            SettingsManager.save_selectors(SELECTORS_SETTINGS)
            return SELECTORS_SETTINGS
        
        try:
            with open(SELLECTORS_FILE, "r") as f:
                selectors = json.load(f)
                # Ensure all default keys exist
                for key, value in SELECTORS_SETTINGS.items():
                    if key not in selectors:
                        selectors[key] = value
                return selectors
        except Exception:
            return SELECTORS_SETTINGS


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

    @staticmethod
    def save_selectors(selectors):
        SettingsManager._ensure_dir()
        try:
            with open(SELLECTORS_FILE, "w") as f:
                json.dump(selectors, f, indent=4)
        except Exception as e:
            print(f"Error saving selectors file: {e}")



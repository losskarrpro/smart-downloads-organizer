import os
import json
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = Path.home() / "Downloads"
ORGANIZED_DIR = DOWNLOADS_DIR / "Organized"
CONFIG_FILE = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "logs"
DAEMON_LOG_FILE = LOG_DIR / "organizer.log"
WEB_LOG_FILE = LOG_DIR / "webserver.log"

# Création des dossiers nécessaires
ORGANIZED_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Catégories par défaut (seront écrasées par config.json)
DEFAULT_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"],
    "Vidéos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php", ".rb", ".json", ".xml"],
    "Musique": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "Installeurs": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk"]
}

# Chargement de la configuration
def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # S'assurer que les chemins sont des Path objects
                if "downloads_path" in config:
                    config["downloads_path"] = Path(config["downloads_path"])
                if "organized_path" in config:
                    config["organized_path"] = Path(config["organized_path"])
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erreur de chargement de config.json: {e}. Utilisation des valeurs par défaut.")
    return {"categories": DEFAULT_CATEGORIES, "downloads_path": DOWNLOADS_DIR, "organized_path": ORGANIZED_DIR}

CONFIG = load_config()

# Paramètres de l'interface web
WEB_HOST = "localhost"
WEB_PORT = 8080
WEB_DEBUG = False

# Paramètres du daemon
SCAN_INTERVAL = 5  # secondes
HISTORY_FILE = LOG_DIR / "history.json"
import json
import os
from pathlib import Path

class Classifier:
    """
    Classifie les fichiers par catégorie selon les règles de configuration.
    """
    
    def __init__(self, config_path=None):
        """
        Initialise le classificateur avec les règles de configuration.
        
        Args:
            config_path (str, optional): Chemin vers le fichier de configuration.
                Si None, cherche config.json dans le répertoire parent.
        """
        if config_path is None:
            # Cherche config.json dans le répertoire parent du projet
            current_dir = Path(__file__).parent
            config_path = current_dir.parent / 'config.json'
        
        self.config_path = Path(config_path)
        self.categories = self._load_config()
    
    def _load_config(self):
        """
        Charge la configuration depuis le fichier JSON.
        
        Returns:
            dict: Dictionnaire des catégories avec leurs extensions.
        
        Raises:
            FileNotFoundError: Si le fichier config.json n'existe pas.
            json.JSONDecodeError: Si le fichier JSON est mal formaté.
        """
        if not self.config_path.exists():
            # Configuration par défaut si fichier non trouvé
            default_config = {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"],
                "Videos": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm", ".m4v", ".mpg", ".mpeg"],
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".md"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz"],
                "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".php", ".rb", ".go", ".rs", ".ts"],
                "Musique": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
                "Installeurs": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk"]
            }
            return default_config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Convertit la configuration en format standard
        categories = {}
        for category, data in config_data.items():
            if isinstance(data, dict) and "extensions" in data:
                categories[category] = data["extensions"]
            elif isinstance(data, list):
                categories[category] = data
            else:
                # Format non reconnu, on ignore
                continue
        
        return categories
    
    def classify(self, filepath):
        """
        Détermine la catégorie d'un fichier.
        
        Args:
            filepath (str or Path): Chemin du fichier à classifier.
        
        Returns:
            str: Nom de la catégorie, ou "Autres" si non reconnu.
        """
        filepath = Path(filepath)
        extension = filepath.suffix.lower()
        
        # Cherche la catégorie correspondant à l'extension
        for category, extensions in self.categories.items():
            if extension in [ext.lower() for ext in extensions]:
                return category
        
        # Catégorie par défaut pour les extensions non reconnues
        return "Autres"
    
    def get_all_categories(self):
        """
        Retourne la liste de toutes les catégories configurées.
        
        Returns:
            list: Liste des noms de catégories.
        """
        return list(self.categories.keys()) + ["Autres"]
    
    def get_category_extensions(self, category):
        """
        Retourne les extensions associées à une catégorie.
        
        Args:
            category (str): Nom de la catégorie.
        
        Returns:
            list: Liste des extensions pour cette catégorie.
        """
        if category == "Autres":
            return []
        return self.categories.get(category, [])
    
    def reload_config(self):
        """
        Recharge la configuration depuis le fichier.
        
        Returns:
            bool: True si rechargement réussi, False sinon.
        """
        try:
            self.categories = self._load_config()
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False
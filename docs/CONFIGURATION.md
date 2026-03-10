# Guide de configuration

## 1. Introduction
Smart Downloads Organizer est un daemon Python qui surveille automatiquement votre dossier de téléchargements et classe les fichiers par catégorie. Ce guide vous explique comment configurer l'application selon vos besoins.

## 2. Structure de configuration
L'application utilise plusieurs fichiers de configuration :

- **config.json** : règles de classification des fichiers
- **config/settings.py** : paramètres généraux de l'application
- **requirements.txt** : dépendances Python requises

## 3. Fichier config.json
Ce fichier définit comment les fichiers sont classés par catégorie. Il se trouve à la racine du projet.

### Structure du fichier
```json
{
  "rules": {
    "Images": {
      "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
      "destination": "Images",
      "organize_by_date": true
    },
    "Videos": {
      "extensions": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"],
      "destination": "Videos",
      "organize_by_date": false
    },
    "Documents": {
      "extensions": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx"],
      "destination": "Documents",
      "organize_by_date": true
    },
    "Archives": {
      "extensions": [".zip", ".rar", ".7z", ".tar", ".gz"],
      "destination": "Archives",
      "organize_by_date": false
    },
    "Code": {
      "extensions": [".py", ".js", ".html", ".css", ".java", ".cpp"],
      "destination": "Code",
      "organize_by_date": true
    },
    "Musique": {
      "extensions": [".mp3", ".wav", ".flac", ".m4a", ".aac"],
      "destination": "Musique",
      "organize_by_date": false
    },
    "Installeurs": {
      "extensions": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
      "destination": "Installeurs",
      "organize_by_date": false
    }
  },
  "default_category": "Divers",
  "organize_existing": false,
  "move_files": true,
  "log_moves": true
}
```

### Paramètres configurables

#### Paramètres par catégorie
- **extensions** : Liste des extensions de fichiers pour cette catégorie
- **destination** : Nom du sous-dossier de destination
- **organize_by_date** : Si true, crée des sous-dossiers par date (AAAA-MM)

#### Paramètres globaux
- **default_category** : Catégorie pour les fichiers non reconnus
- **organize_existing** : Si true, organise les fichiers existants au démarrage
- **move_files** : Si true, déplace les fichiers (sinon copie)
- **log_moves** : Si true, enregistre les déplacements dans le journal

## 4. Personnalisation des règles

### Ajouter une nouvelle catégorie
1. Ouvrez `config.json`
2. Ajoutez un nouvel objet dans la section "rules" :
```json
"NouvelleCategorie": {
  "extensions": [".ext1", ".ext2"],
  "destination": "NomDossier",
  "organize_by_date": false
}
```

### Modifier les extensions
- Ajoutez ou supprimez des extensions dans les tableaux existants
- Les extensions sont sensibles à la casse (utilisez des minuscules)

### Organiser par date
- Quand `organize_by_date` est true, les fichiers sont placés dans `Dossier/AAAA-MM/`
- Exemple : `Downloads/Images/2024-03/photo.jpg`

## 5. Configuration du dossier de surveillance
Le dossier surveillé est configuré dans `config/settings.py` :

```python
# Dossier à surveiller (par défaut: le dossier Downloads de l'utilisateur)
DOWNLOADS_FOLDER = os.path.expanduser("~/Downloads")

# Dossier de destination (par défaut: même que DOWNLOADS_FOLDER)
DESTINATION_BASE = DOWNLOADS_FOLDER

# Ignorer les fichiers temporaires
IGNORE_PATTERNS = ["*.tmp", "*.temp", "*.crdownload", "*.part"]
```

### Changer le dossier surveillé
Modifiez la variable `DOWNLOADS_FOLDER` dans `config/settings.py` :
```python
DOWNLOADS_FOLDER = "/chemin/vers/votre/dossier"
```

## 6. Configuration du serveur web
L'interface web est configurable via `config/settings.py` :

```python
# Configuration du serveur web
WEB_HOST = "localhost"
WEB_PORT = 8080
WEB_DEBUG = False

# Intervalle de rafraîchissement des statistiques (en secondes)
STATS_REFRESH_INTERVAL = 30

# Nombre maximum d'entrées dans l'historique
MAX_HISTORY_ENTRIES = 100
```

### Accéder à l'interface web
- URL : `http://localhost:8080`
- Pour changer le port, modifiez `WEB_PORT`
- Pour autoriser l'accès réseau, changez `WEB_HOST` en `"0.0.0.0"`

## 7. Gestion des logs
Les logs sont configurés dans `config/settings.py` :

```python
# Fichiers de logs
LOG_FILE = "logs/organizer.log"
WEB_LOG_FILE = "logs/webserver.log"

# Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# Taille maximale des fichiers de log (en octets)
MAX_LOG_SIZE = 10485760  # 10 Mo

# Nombre de fichiers de log à conserver
BACKUP_COUNT = 5
```

### Visualiser les logs
- Logs de l'organiseur : `logs/organizer.log`
- Logs du serveur web : `logs/webserver.log`
- Les logs sont automatiquement archivés lorsqu'ils atteignent 10 Mo

## 8. Base de données
La base de données SQLite est configurée dans `config/settings.py` :

```python
# Configuration de la base de données
DATABASE_FILE = "database/organizer.db"

# Activer/désactiver la base de données
USE_DATABASE = True

# Durée de conservation des données (en jours)
DATA_RETENTION_DAYS = 365
```

### Réinitialiser la base de données
Supprimez le fichier `database/organizer.db` et redémarrez l'application.

## 9. Installation en tant que service (Linux)

### Installation
```bash
sudo bash scripts/install_service.sh
```

### Désinstallation
```bash
sudo bash scripts/uninstall_service.sh
```

### Configuration du service
Le service peut être configuré via :
- `scripts/smart-downloads-organizer.service` (fichier systemd)
- Modifiez `User=` et `WorkingDirectory=` selon votre installation

## 10. Dépannage

### Problèmes courants

1. **L'application ne démarre pas**
   - Vérifiez que Python 3.8+ est installé
   - Exécutez `pip install -r requirements.txt`

2. **Les fichiers ne sont pas déplacés**
   - Vérifiez les permissions d'écriture
   - Consultez `logs/organizer.log` pour les erreurs

3. **L'interface web n'est pas accessible**
   - Vérifiez que le port n'est pas déjà utilisé
   - Consultez `logs/webserver.log`

4. **Règles de classification non appliquées**
   - Vérifiez la syntaxe de `config.json`
   - Redémarrez l'application après modification

### Mode debug
Activez le mode debug dans `config/settings.py` :
```python
LOG_LEVEL = "DEBUG"
WEB_DEBUG = True
```

## 11. Mise à jour de la configuration
Après toute modification de configuration :
1. Redémarrez l'application
2. Pour les modifications de `config.json`, un redémarrage est nécessaire
3. Pour les modifications de `config/settings.py`, un redémarrage est nécessaire

## 12. Configuration avancée
### Variables d'environnement
L'application supporte les variables d'environnement :
- `SDO_DOWNLOADS_FOLDER` : Remplace `DOWNLOADS_FOLDER`
- `SDO_WEB_PORT` : Remplace `WEB_PORT`
- `SDO_LOG_LEVEL` : Remplace `LOG_LEVEL`

### Exécution avec Docker
Consultez `docs/DOCKER.md` pour la configuration Docker.

## 13. Support
Pour plus d'aide :
- Consultez `docs/API.md` pour l'API interne
- Vérifiez les fichiers de logs
- Ouvrez une issue sur le dépôt GitHub
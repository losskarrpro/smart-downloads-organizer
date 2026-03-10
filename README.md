# Smart Downloads Organizer

## Description
Smart Downloads Organizer est un démon Python intelligent qui surveille en temps réel votre dossier de téléchargements et organise automatiquement les fichiers par catégories. Il utilise watchdog pour la surveillance, un système de règles configurables, et inclut une interface web pour consulter les statistiques et l'historique.

## Fonctionnalités
- Surveillance en temps réel du dossier Downloads avec watchdog
- Classification automatique des fichiers par catégories (Images, Vidéos, Documents, Archives, Code, Musique, Installeurs)
- Configuration flexible via fichier JSON
- Interface web intuitive avec statistiques en temps réel
- Historique complet des opérations avec horodatage
- Base de données SQLite pour le suivi des activités
- Installation en tant que service système (Linux/Mac)
- Tests unitaires et d'intégration complets

## Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)

### Installation automatique
```bash
# Clonez le dépôt
git clone https://github.com/votre-utilisateur/smart-downloads-organizer.git
cd smart-downloads-organizer

# Installez les dépendances
pip install -r requirements.txt

# Exécutez le script d'installation du service (Linux/Mac)
sudo bash scripts/install_service.sh
```

### Installation manuelle
```bash
# Installez les dépendances
pip install watchdog flask sqlite3

# Lancez l'application
python run.py
```

## Configuration

### Fichier config.json
Modifiez `config.json` pour personnaliser les règles de classification :

```json
{
    "watch_folder": "/chemin/vers/votre/dossier/Downloads",
    "destination_base": "/chemin/vers/dossier/organisé",
    "rules": {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "Vidéos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp"],
        "Musique": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
        "Installeurs": [".exe", ".msi", ".dmg", ".pkg", ".deb"]
    },
    "log_file": "logs/organizer.log",
    "web_interface": {
        "host": "localhost",
        "port": 8080,
        "debug": false
    }
}
```

## Utilisation

### Lancement manuel
```bash
python run.py
```

### Démarrage du service (Linux/Mac)
```bash
sudo systemctl start smart-downloads-organizer
```

### Arrêt du service
```bash
sudo systemctl stop smart-downloads-organizer
```

### Interface web
Accédez à l'interface web à l'adresse : `http://localhost:8080`

L'interface propose :
- Tableau de bord avec statistiques
- Historique des fichiers organisés
- Graphiques de répartition par catégorie
- Gestion des règles en temps réel

## Structure du projet
```
smart-downloads-organizer/
├── organizer.py              # Démon principal avec watchdog
├── config.json              # Règles de classification
├── web_interface.py         # Serveur web Flask
├── templates/               # Templates HTML
│   ├── index.html          # Page principale
│   ├── stats.html          # Page de statistiques
│   └── history.html        # Page d'historique
├── static/                  # Fichiers statiques
│   ├── css/style.css       # Feuilles de style
│   └── js/charts.js        # Scripts JavaScript
├── utils/                   # Utilitaires
│   ├── classifier.py       # Classificateur de fichiers
│   └── file_handler.py     # Gestionnaire de fichiers
├── models/                  # Modèles de données
│   └── stats.py            # Modèle des statistiques
├── database/                # Gestion de base de données
│   ├── schema.sql          # Schéma SQLite
│   └── db_manager.py       # Gestionnaire de base de données
├── config/                  # Configuration
│   └── settings.py         # Paramètres de l'application
├── logs/                   # Journaux d'activité
│   ├── organizer.log       # Journal du démon
│   └── webserver.log       # Journal du serveur web
├── scripts/                # Scripts système
│   ├── install_service.sh  # Installation du service
│   └── uninstall_service.sh # Désinstallation du service
├── tests/                  # Tests unitaires
│   ├── test_classifier.py  # Tests du classificateur
│   ├── test_file_handler.py # Tests du gestionnaire
│   ├── test_web_interface.py # Tests de l'interface web
│   └── test_integration.py # Tests d'intégration
├── docs/                   # Documentation
│   ├── API.md             # Documentation API
│   └── CONFIGURATION.md   # Guide de configuration
├── requirements.txt        # Dépendances Python
├── setup.py               # Configuration du package
├── run.py                 Point d'entrée de l'application
└── README.md              # Ce fichier
```

## Tests

### Exécution des tests
```bash
# Tests unitaires
python -m pytest tests/test_classifier.py -v
python -m pytest tests/test_file_handler.py -v

# Tests de l'interface web
python -m pytest tests/test_web_interface.py -v

# Tests d'intégration
python -m pytest tests/test_integration.py -v
```

## Développement

### Contribution
1. Forkez le projet
2. Créez une branche de fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

### Dépendances de développement
```bash
pip install -r requirements.txt
pip install pytest pytest-cov  # Pour les tests
```

## Support
Pour signaler un bug ou demander une fonctionnalité, veuillez ouvrir une issue sur le dépôt GitHub.

## Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Auteurs
- Équipe Smart Downloads Organizer

## Remerciements
- Watchdog pour la surveillance de fichiers
- Flask pour l'interface web
- Tous les contributeurs
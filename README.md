# Smart Downloads Organizer

**Créé par LUMENA**

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
│   └── config_manager.py   # Gestionnaire de configuration
├── logs/                    # Fichiers de log
├── tests/                   # Tests unitaires
│   ├── test_classifier.py
│   ├── test_organizer.py
│   └── test_web_interface.py
├── scripts/                 # Scripts utilitaires
│   ├── install_service.sh  # Installation service Linux/Mac
│   └── uninstall_service.sh
├── requirements.txt         # Dépendances Python
├── run.py                   # Point d'entrée principal
└── README.md                # Documentation
```

## Développement

### Exécution des tests
```bash
python -m pytest tests/
```

### Contribution
Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour discuter des changements proposés.

## Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
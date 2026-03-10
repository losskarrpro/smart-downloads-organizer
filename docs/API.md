# Documentation de l'API Web - Smart Downloads Organizer

## Introduction

L'API web du Smart Downloads Organizer fournit un accès programmatique aux données de l'organisateur via des endpoints RESTful. Elle permet de récupérer des statistiques, l'historique des fichiers traités, et de contrôler certaines fonctionnalités du daemon.

## Base URL

Tous les endpoints sont accessibles à partir de la base URL : `http://localhost:5000/api`

## Authentification

Actuellement, l'API ne nécessite pas d'authentification car elle est conçue pour être utilisée localement.

## Format des réponses

Les réponses sont au format JSON avec les clés suivantes :
- `success` : booléen indiquant si la requête a réussi
- `data` : contient les données de la réponse (si `success` est true)
- `error` : contient le message d'erreur (si `success` est false)

Exemple de réponse réussie :
```json
{
  "success": true,
  "data": {
    "total_files": 42
  }
}
```

Exemple d'erreur :
```json
{
  "success": false,
  "error": "Fichier non trouvé"
}
```

## Endpoints

### 1. Statistiques

#### GET /api/stats
Récupère les statistiques globales de l'organisateur.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "total_files_processed": 150,
    "by_category": {
      "Images": 45,
      "Documents": 32,
      "Videos": 28,
      "Archives": 15,
      "Code": 12,
      "Music": 10,
      "Installers": 8
    },
    "total_size_processed": "2.4 GB",
    "organizer_status": "running",
    "last_processed": "2023-10-15 14:30:22",
    "files_today": 12
  }
}
```

#### GET /api/stats/recent
Récupère les statistiques des dernières 24 heures.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "files_last_24h": 12,
    "size_last_24h": "450 MB",
    "by_hour": [
      {"hour": "00:00", "count": 0},
      {"hour": "01:00", "count": 0},
      // ... autres heures
      {"hour": "14:00", "count": 5},
      {"hour": "15:00", "count": 7}
    ]
  }
}
```

### 2. Historique

#### GET /api/history
Récupère l'historique des fichiers traités.

**Paramètres de requête :**
- `limit` (optionnel) : Nombre maximum d'entrées à retourner (défaut: 50, max: 1000)
- `offset` (optionnel) : Décalage pour la pagination (défaut: 0)
- `category` (optionnel) : Filtrer par catégorie
- `date_from` (optionnel) : Date de début (format: YYYY-MM-DD)
- `date_to` (optionnel) : Date de fin (format: YYYY-MM-DD)

**Réponse :**
```json
{
  "success": true,
  "data": {
    "total_entries": 150,
    "limit": 50,
    "offset": 0,
    "history": [
      {
        "id": 142,
        "timestamp": "2023-10-15 14:30:22",
        "filename": "document.pdf",
        "original_path": "/home/user/Downloads/document.pdf",
        "new_path": "/home/user/Downloads/Documents/document.pdf",
        "category": "Documents",
        "file_size": "2.4 MB",
        "status": "moved"
      },
      // ... autres entrées
    ]
  }
}
```

#### GET /api/history/{id}
Récupère les détails d'une entrée spécifique de l'historique.

**Paramètres d'URL :**
- `id` : ID de l'entrée dans l'historique

**Réponse :**
```json
{
  "success": true,
  "data": {
    "id": 142,
    "timestamp": "2023-10-15 14:30:22",
    "filename": "document.pdf",
    "original_path": "/home/user/Downloads/document.pdf",
    "new_path": "/home/user/Downloads/Documents/document.pdf",
    "category": "Documents",
    "file_size": "2516582",
    "file_size_human": "2.4 MB",
    "file_extension": ".pdf",
    "status": "moved",
    "checksum": "a1b2c3d4e5f6..."
  }
}
```

### 3. Fichiers

#### GET /api/files
Récupère la liste des fichiers actuellement dans le dossier Downloads.

**Paramètres de requête :**
- `category` (optionnel) : Filtrer par catégorie
- `sort` (optionnel) : Critère de tri (name, size, date) (défaut: date)
- `order` (optionnel) : Ordre de tri (asc, desc) (défaut: desc)

**Réponse :**
```json
{
  "success": true,
  "data": {
    "total_files": 8,
    "files": [
      {
        "name": "photo.jpg",
        "path": "/home/user/Downloads/Images/photo.jpg",
        "category": "Images",
        "size": "4.2 MB",
        "size_bytes": 4404019,
        "modified": "2023-10-15 14:25:11",
        "extension": ".jpg"
      },
      // ... autres fichiers
    ]
  }
}
```

#### POST /api/files/process
Force le traitement immédiat d'un fichier spécifique.

**Corps de la requête (JSON) :**
```json
{
  "file_path": "/chemin/complet/vers/fichier.txt"
}
```

**Réponse :**
```json
{
  "success": true,
  "data": {
    "message": "Fichier traité avec succès",
    "original_path": "/chemin/complet/vers/fichier.txt",
    "new_path": "/chemin/complet/vers/Documents/fichier.txt",
    "category": "Documents"
  }
}
```

### 4. Catégories

#### GET /api/categories
Récupère la liste des catégories configurées.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "name": "Images",
        "folder": "Images",
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
        "file_count": 45,
        "total_size": "850 MB"
      },
      // ... autres catégories
    ]
  }
}
```

#### GET /api/categories/{category_name}
Récupère les détails d'une catégorie spécifique.

**Paramètres d'URL :**
- `category_name` : Nom de la catégorie

**Réponse :**
```json
{
  "success": true,
  "data": {
    "name": "Images",
    "folder": "Images",
    "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "file_count": 45,
    "total_size": "850 MB",
    "total_size_bytes": 891289600,
    "last_addition": "2023-10-15 14:25:11"
  }
}
```

### 5. Configuration

#### GET /api/config
Récupère la configuration actuelle.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "downloads_path": "/home/user/Downloads",
    "organizer_settings": {
      "watch_subdirectories": false,
      "move_files": true,
      "create_folders": true,
      "log_level": "INFO"
    },
    "categories": [
      {
        "name": "Images",
        "folder": "Images",
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"]
      },
      // ... autres catégories
    ],
    "web_interface": {
      "host": "127.0.0.1",
      "port": 5000,
      "debug": false
    }
  }
}
```

#### PUT /api/config
Met à jour la configuration (une partie ou la totalité).

**Corps de la requête (JSON) :**
```json
{
  "organizer_settings": {
    "log_level": "DEBUG"
  }
}
```

**Réponse :**
```json
{
  "success": true,
  "data": {
    "message": "Configuration mise à jour avec succès",
    "restart_required": false
  }
}
```

### 6. Contrôle du daemon

#### GET /api/daemon/status
Récupère le statut du daemon.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "status": "running",
    "pid": 12345,
    "uptime": "2 jours, 5 heures, 12 minutes",
    "version": "1.0.0",
    "last_heartbeat": "2023-10-15 14:45:00"
  }
}
```

#### POST /api/daemon/restart
Redémarre le daemon.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "message": "Daemon redémarré avec succès"
  }
}
```

#### POST /api/daemon/stop
Arrête le daemon.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "message": "Daemon arrêté avec succès"
  }
}
```

#### POST /api/daemon/start
Démarre le daemon.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "message": "Daemon démarré avec succès"
  }
}
```

### 7. Logs

#### GET /api/logs
Récupère les logs de l'application.

**Paramètres de requête :**
- `type` (optionnel) : Type de logs (organizer, webserver, all) (défaut: organizer)
- `limit` (optionnel) : Nombre maximum de lignes (défaut: 100, max: 1000)
- `level` (optionnel) : Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `search` (optionnel) : Terme de recherche dans les logs

**Réponse :**
```json
{
  "success": true,
  "data": {
    "log_type": "organizer",
    "total_lines": 1245,
    "limit": 100,
    "logs": [
      "2023-10-15 14:30:22 INFO - Fichier 'document.pdf' déplacé vers 'Documents'",
      "2023-10-15 14:25:11 INFO - Fichier 'photo.jpg' déplacé vers 'Images'",
      // ... autres lignes de log
    ]
  }
}
```

### 8. Système

#### GET /api/system/info
Récupère des informations sur le système.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "system": {
      "platform": "Linux",
      "hostname": "desktop-pc",
      "python_version": "3.9.12"
    },
    "disk_usage": {
      "downloads_folder": {
        "total": "500 GB",
        "used": "120 GB",
        "free": "380 GB",
        "percent": 24
      },
      "system": {
        "total": "1 TB",
        "used": "350 GB",
        "free": "650 GB",
        "percent": 35
      }
    },
    "memory_usage": {
      "total": "16 GB",
      "available": "8 GB",
      "percent": 50
    }
  }
}
```

## Codes d'erreur HTTP

- `200 OK` : Requête réussie
- `400 Bad Request` : Paramètres de requête invalides
- `404 Not Found` : Ressource non trouvée
- `405 Method Not Allowed` : Méthode HTTP non autorisée pour l'endpoint
- `500 Internal Server Error` : Erreur interne du serveur

## Exemples d'utilisation

### Récupérer les statistiques avec curl
```bash
curl -X GET "http://localhost:5000/api/stats"
```

### Forcer le traitement d'un fichier
```bash
curl -X POST "http://localhost:5000/api/files/process" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/home/user/Downloads/new_file.zip"}'
```

### Récupérer l'historique avec des paramètres
```bash
curl -X GET "http://localhost:5000/api/history?limit=10&category=Images"
```

## Notes

- L'API est conçue pour un usage local et n'est pas sécurisée pour une exposition sur Internet.
- Toutes les dates et heures sont au format ISO 8601 (YYYY-MM-DD HH:MM:SS) en temps local.
- Les tailles de fichiers sont renvoyées sous forme lisible par l'homme (ex: "2.4 MB") et en octets dans le champ `size_bytes`.
- Le daemon doit être en cours d'exécution pour que certains endpoints fonctionnent (comme les contrôles du daemon).
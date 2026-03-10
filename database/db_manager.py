```python
import sqlite3
import logging
import os
from datetime import datetime
from contextlib import contextmanager

# Configuration du logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestionnaire de base de données SQLite pour le suivi des fichiers."""
    
    def __init__(self, db_path=None):
        """
        Initialise le gestionnaire de base de données.
        
        Args:
            db_path (str, optional): Chemin vers la base de données.
                Par défaut: 'smart_downloads.db' dans le répertoire courant.
        """
        if db_path is None:
            # Chemin par défaut dans le dossier database
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(current_dir, 'smart_downloads.db')
        else:
            self.db_path = db_path
        
        # Crée le dossier parent si nécessaire
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialise la base de données
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager pour obtenir une connexion à la base de données."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Pour obtenir des dictionnaires
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Erreur base de données: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialise la base de données et crée les tables si nécessaire."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table des événements de fichiers
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    filename TEXT NOT NULL,
                    original_path TEXT NOT NULL,
                    new_path TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER,
                    operation TEXT NOT NULL
                )
            ''')
            
            # Table des statistiques par catégorie
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS category_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    category TEXT NOT NULL,
                    file_count INTEGER DEFAULT 0,
                    total_size INTEGER DEFAULT 0,
                    UNIQUE(date, category)
                )
            ''')
            
            # Table des extensions fréquentes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS extension_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    extension TEXT NOT NULL,
                    count INTEGER DEFAULT 0,
                    UNIQUE(date, extension)
                )
            ''')
            
            # Index pour les performances
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_events_timestamp ON file_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_events_file_type ON file_events(file_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category_stats_date ON category_stats(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_extension_stats_date ON extension_stats(date)')
            
            logger.info(f"Base de données initialisée: {self.db_path}")
    
    def log_file_event(self, filename, original_path, new_path, file_type, file_size=None, operation="move"):
        """
        Enregistre un événement de déplacement de fichier.
        
        Args:
            filename (str): Nom du fichier
            original_path (str): Chemin d'origine
            new_path (str): Nouveau chemin
            file_type (str): Type/catégorie du fichier
            file_size (int, optional): Taille du fichier en octets
            operation (str): Type d'opération (move, delete, etc.)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Extraire l'extension du fichier
            _, ext = os.path.splitext(filename)
            extension = ext.lower() if ext else 'sans_extension'
            
            # Enregistrer l'événement
            cursor.execute('''
                INSERT INTO file_events 
                (timestamp, filename, original_path, new_path, file_type, file_size, operation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                filename,
                original_path,
                new_path,
                file_type,
                file_size,
                operation
            ))
            
            # Mettre à jour les statistiques quotidiennes
            today = datetime.now().date().isoformat()
            
            # Statistiques par catégorie
            cursor.execute('''
                INSERT INTO category_stats (date, category, file_count, total_size)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(date, category) DO UPDATE SET
                file_count = file_count + 1,
                total_size = total_size + excluded.total_size
            ''', (today, file_type, file_size or 0))
            
            # Statistiques par extension
            cursor.execute('''
                INSERT INTO extension_stats (date, extension, count)
                VALUES (?, ?, 1)
                ON CONFLICT(date, extension) DO UPDATE SET
                count = count + 1
            ''', (today, extension))
            
            logger.debug(f"Événement enregistré: {filename} -> {file_type}")
    
    def get_recent_events(self, limit=100):
        """
        Récupère les événements récents.
        
        Args:
            limit (int): Nombre maximum d'événements à récupérer
            
        Returns:
            list: Liste d'événements récents
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM file_events
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_category_stats(self, days=30):
        """
        Récupère les statistiques par catégorie sur une période.
        
        Args:
            days (int): Nombre de jours à inclure
            
        Returns:
            dict: Statistiques par catégorie
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Statistiques globales
            cursor.execute('''
                SELECT 
                    category,
                    COUNT(*) as file_count,
                    SUM(file_size) as total_size
                FROM file_events
                WHERE timestamp >= date('now', ? || ' days')
                GROUP BY category
                ORDER BY file_count DESC
            ''', (f"-{days}",))
            
            stats = {}
            for row in cursor.fetchall():
                category = row['category']
                stats[category] = {
                    'file_count': row['file_count'],
                    'total_size': row['total_size'] or 0,
                    'avg_size': (row['total_size'] or 0) // max(row['file_count'], 1)
                }
            
            return stats
    
    def get_daily_stats(self, days=30):
        """
        Récupère les statistiques quotidiennes.
        
        Args:
            days (int): Nombre de jours à inclure
            
        Returns:
            list: Statistiques par jour
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    date,
                    SUM(file_count) as total_files,
                    SUM(total_size) as total_size
                FROM category_stats
                WHERE date >= date('now', ? || ' days')
                GROUP BY date
                ORDER BY date DESC
            ''', (f"-{days}",))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_extension_stats(self, limit=20):
        """
        Récupère les statistiques des extensions les plus fréquentes.
        
        Args:
            limit (int): Nombre d'extensions à inclure
            
        Returns:
            list: Statistiques par extension
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    extension,
                    SUM(count) as total_count
                FROM extension_stats
                GROUP BY extension
                ORDER BY total_count DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def search_events(self, query=None, file_type=None, start_date=None, end_date=None, limit=100):
        """
        Recherche des événements avec des filtres.
        
        Args:
            query (str, optional): Recherche textuelle dans les noms de fichiers
            file_type (str, optional): Filtre par type de fichier
            start_date (str, optional): Date de début (format ISO)
            end_date (str, optional): Date de fin (format ISO)
            limit (int): Limite de résultats
            
        Returns:
            list: Événements correspondants aux critères
        """
        with self._get_connection() as conn:
            cursor =cursor.execute('''
                SELECT * FROM file_events
                WHERE 1=1
                {} {} {} {}
                ORDER BY timestamp DESC
                LIMIT ?
            '''.format(
                f"AND filename LIKE '%{query}%'" if query else "",
                f"AND file_type = '{file_type}'" if file_type else "",
                f"AND timestamp >= '{start_date}'" if start_date else "",
                f"AND timestamp <= '{end_date}'" if end_date else ""
            ), (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_total_stats(self):
        """
        Récupère les statistiques globales.
        
        Returns:
            dict: Statistiques globales
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as total_files FROM file_events')
            total_files = cursor.fetchone()['total_files']
            
            cursor.execute('SELECT SUM(file_size) as total_size FROM file_events')
            total_size = cursor.fetchone()['total_size'] or 0
            
            cursor.execute('SELECT COUNT(DISTINCT file_type) as categories FROM file_events')
            categories = cursor.fetchone()['categories']
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'categories': categories
            }
    
    def clear_old_events(self, days_to_keep=365):
        """
        Supprime les événements plus anciens qu'un certain nombre de jours.
        
        Args:
            days_to_keep (int): Nombre de jours à conserver
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            delete_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            cursor.execute('''
                DELETE FROM file_events 
                WHERE timestamp < ?
            ''', (delete_date,))
            
            cursor.execute('''
                DELETE FROM category_stats 
                WHERE date < date('now', ? || ' days')
            ''', (f"-{days_to_keep}",))
            
            cursor.execute('''
                DELETE FROM extension_stats 
                WHERE date < date('now', ? || ' days')
            ''', (f"-{days_to_keep}",))
            
            deleted_count = cursor.rowcount
            logger.info(f"{deleted_count} anciens événements supprimés (plus de {days_to_keep} jours)")
    
    def export_to_csv(self, output_path):
        """
        Exporte les événements vers un fichier CSV.
        
        Args:
            output_path (str): Chemin du fichier CSV de sortie
        """
        import csv
        
        events = self.get_recent_events(limit=1000000)  # Tous les événements
        
        if not events:
            logger.warning("Aucun événement à exporter")
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = events[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(events)
        
        logger.info(f"{len(events)} événements exportés vers {output_path}")
    
    def backup_database(self, backup_path=None):
        """
        Crée une sauvegarde de la base de données.
        
        Args:
            backup_path (str, optional): Chemin de la sauvegarde
        """
        import shutil
        
        if backup_path is None:
            backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'smart_downloads_{timestamp}.db')
        
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Base de données sauvegardée: {backup_path}")
        return backup_path

# Singleton pour faciliter l'utilisation
_db_instance = None

def get_db_manager(db_path=None):
    """
    Retourne une instance singleton du gestionnaire de base de données.
    
    Args:
        db_path (str, optional): Chemin vers la base de données
        
    Returns:
        DatabaseManager: Instance du gestionnaire
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager(db_path)
    return _db_instance

# Test rapide si exécuté directement
if __name__ == "__main__":
    # Configuration du logging pour le test
    logging.basicConfig(level=logging.INFO)
    
    # Test de la base de données
    db = DatabaseManager(":memory:")  # Base de données en mémoire pour le test
    
    # Test d'insertion
    db.log_file_event(
        filename="test.jpg",
        original_path="/tmp/test.jpg",
        new_path="/tmp/Images/test.jpg",
        file_type="Images",
        file_size=1024,
        operation="move"
    )
    
    # Test de récupération
    events = db.get_recent_events()
    print(f"Événements récents: {len(events)}")
    
    stats = db.get_category_stats()
    print(f"Statistiques par catégorie: {stats}")
    
    total = db.get_total_stats()
    print(f"Statistiques globales: {total}")
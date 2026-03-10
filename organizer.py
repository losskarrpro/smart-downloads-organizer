# Fichier : organizer.py
# Description : Daemon principal avec watchdog pour surveiller le dossier Downloads en temps réel et classer automatiquement les fichiers.
# Contenu : Utilise watchdog pour détecter les changements, utilise les modules du projet pour classifier et déplacer les fichiers.
#           Inclut la journalisation, la gestion de configuration et le démarrage du daemon.

import os
import sys
import json
import time
import logging
from pathlib import Path
from threading import Event
from signal import signal, SIGINT, SIGTERM

# Import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import des modules internes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.classifier import classify_file
from utils.file_handler import move_file
from models.stats import Stats
from config.settings import get_config

# Configuration du logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'organizer.log')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DownloadHandler(FileSystemEventHandler):
    """Handler pour les événements de fichiers dans le dossier Downloads."""

    def __init__(self, config, stats):
        super().__init__()
        self.config = config
        self.stats = stats
        self.downloads_path = Path(self.config['downloads_folder'])
        # Liste des extensions en cours de traitement pour éviter les doubles traitements
        self.processing_files = set()

    def on_created(self, event):
        """Appelé quand un fichier est créé (ou déplacé dans le dossier)."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        # Attendre que le fichier soit complètement écrit (taille stable)
        time.sleep(self.config.get('file_stability_delay', 2))

        # Vérifier si le fichier existe toujours et n'est pas en cours de traitement
        if not file_path.exists():
            logger.warning(f"File {file_path} no longer exists, skipping.")
            return

        if file_path.name in self.processing_files:
            logger.debug(f"File {file_path.name} is already being processed.")
            return

        self.processing_files.add(file_path.name)
        try:
            self.process_file(file_path)
        finally:
            self.processing_files.remove(file_path.name)

    def process_file(self, file_path):
        """Traite un fichier : classification et déplacement."""
        # Classification
        category = classify_file(file_path, self.config)
        if category is None:
            logger.info(f"No category found for {file_path.name}, leaving in place.")
            return

        # Déterminer le dossier de destination
        dest_folder_name = self.config['categories'].get(category, {}).get('folder', category)
        dest_path = Path(self.config['organize_root']) / dest_folder_name
        dest_path.mkdir(parents=True, exist_ok=True)

        # Déplacer le fichier
        result = move_file(file_path, dest_path, self.config.get('conflict_resolution', 'rename'))
        if result:
            logger.info(f"Moved {file_path.name} to {dest_path}")
            # Mettre à jour les statistiques
            self.stats.increment(category)
            # Enregistrer dans l'historique
            self.stats.log_move(file_path.name, str(dest_path), category)
        else:
            logger.error(f"Failed to move {file_path.name}")

class OrganizerDaemon:
    """Daemon principal pour organiser les téléchargements."""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        self.config = get_config(config_path)
        self.stats = Stats()
        self.observer = Observer()
        self.stop_event = Event()
        self.handler = DownloadHandler(self.config, self.stats)

    def run(self):
        """Lance le daemon."""
        logger.info("Starting Smart Downloads Organizer Daemon")
        downloads_path = Path(self.config['downloads_folder'])
        if not downloads_path.exists():
            logger.error(f"Downloads folder does not exist: {downloads_folder}")
            sys.exit(1)

        # Planifier l'observation du dossier Downloads
        self.observer.schedule(self.handler, str(downloads_path), recursive=False)
        self.observer.start()

        logger.info(f"Monitoring {downloads_path} for changes...")

        # Gestion des signaux pour un arrêt propre
        signal(SIGINT, self.signal_handler)
        signal(SIGTERM, self.signal_handler)

        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def signal_handler(self, signum, frame):
        """Gère les signaux d'arrêt."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop_event.set()

    def shutdown(self):
        """Arrête le daemon proprement."""
        self.observer.stop()
        self.observer.join()
        logger.info("Daemon stopped.")

def main():
    """Point d'entrée principal."""
    daemon = OrganizerDaemon()
    daemon.run()

if __name__ == '__main__':
    main()
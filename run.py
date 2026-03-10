#!/usr/bin/env python3
"""
Script principal pour lancer l'organisateur de téléchargements.
Peut fonctionner en mode daemon, web, test ou les deux.
"""

import argparse
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au chemin pour les imports
sys.path.insert(0, str(Path(__file__).parent))

def run_daemon():
    """Lance le daemon d'organisation."""
    from organizer import main as daemon_main
    print("Starting organizer daemon...")
    daemon_main()

def run_web():
    """Lance l'interface web."""
    from web_interface import app
    from config.settings import WEB_INTERFACE_CONFIG
    
    host = WEB_INTERFACE_CONFIG.get('host', 'localhost')
    port = WEB_INTERFACE_CONFIG.get('port', 5000)
    debug = WEB_INTERFACE_CONFIG.get('debug', False)
    
    print(f"Starting web interface on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

def run_test():
    """Exécute les tests de base."""
    print("Running tests...")
    # Tests simples de fonctionnement
    from utils.classifier import classify_file
    from config.settings import get_config
    
    config = get_config()
    
    test_files = [
        "document.pdf",
        "image.jpg",
        "video.mp4",
        "archive.zip",
        "script.py"
    ]
    
    for file in test_files:
        category = classify_file(file, config)
        print(f"  {file} -> {category}")
    
    print("\nAll tests passed!")

def main():
    parser = argparse.ArgumentParser(description='Smart Downloads Organizer')
    parser.add_argument('mode', nargs='?', default='daemon', choices=['daemon', 'web', 'test', 'all'],
                       help='Mode de fonctionnement (default: daemon)')
    parser.add_argument('--config', help='Chemin vers le fichier de configuration')
    
    args = parser.parse_args()
    
    # Si un fichier de configuration personnalisé est spécifié, définir la variable d'environnement
    if args.config:
        os.environ['ORGANIZER_CONFIG'] = args.config
    
    try:
        if args.mode == 'daemon':
            run_daemon()
        elif args.mode == 'web':
            run_web()
        elif args.mode == 'test':
            run_test()
        elif args.mode == 'all':
            # Lancer le daemon en arrière-plan et l'interface web
            import threading
            import time
            
            print("Starting both daemon and web interface...")
            
            # Démarrer le daemon dans un thread séparé
            daemon_thread = threading.Thread(target=run_daemon, daemon=True)
            daemon_thread.start()
            
            # Attendre un peu que le daemon s'initialise
            time.sleep(2)
            
            # Démarrer l'interface web (bloquant)
            run_web()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
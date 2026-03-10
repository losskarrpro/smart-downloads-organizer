Nous allons écrire des tests d'intégration qui testent l'ensemble du système.
 Ces tests vont simuler l'ajout de fichiers dans un dossier de test et vérifier qu'ils sont bien classés.
 Nous allons utiliser un répertoire temporaire pour les tests.

 Plan des tests d'intégration :
 1. Test de l'installation du watchdog et de la détection de fichier.
 2. Test du classement des fichiers en fonction des règles de config.json.
 3. Test de la mise à jour des statistiques et de l'interface web.

 Cependant, notez que nous testons l'intégration, donc nous allons lancer le daemon dans un thread séparé,
 puis ajouter des fichiers dans le dossier surveillé et vérifier qu'ils sont bien déplacés.

 Étant donné que le daemon principal est dans organizer.py, nous allons l'importer et lancer la surveillance dans un dossier temporaire.

 Pour éviter de modifier le vrai dossier Downloads, nous allons créer un répertoire temporaire pour les tests.

 Nous allons également créer une configuration temporaire pour les tests.

 Nous allons structurer le test comme suit :

 - Créer un répertoire temporaire pour le dossier "Downloads" de test et les dossiers de destination.
 - Créer un fichier config.json temporaire avec des règles de test.
 - Démarrer le daemon dans un thread séparé.
 - Créer un fichier dans le dossier surveillé.
 - Attendre un moment pour que le daemon traite le fichier.
 - Vérifier que le fichier a été déplacé dans le bon dossier de destination.
 - Arrêter le daemon.

 Nous allons utiliser le module tempfile pour créer les répertoires temporaires.

 Attention: le daemon utilise un observer de watchdog, nous devons pouvoir l'arrêter proprement.

 Nous allons également tester que les statistiques sont mises à jour (en utilisant les modèles de stats).

 Cependant, pour ne pas trop complexifier, nous allons nous concentrer sur le déplacement de fichiers.

 Nous allons écrire plusieurs tests pour différentes catégories.

 Note: pour éviter les problèmes de timing, nous pouvons utiliser des attentes actives avec un timeout.

 Nous allons également tester l'interface web en lançant le serveur web dans un thread séparé et en faisant des requêtes.

 Mais d'abord, concentrons-nous sur le déplacement de fichiers.

 Étapes:

 1. Imports nécessaires.
 2. Création d'une classe de test.
 3. Méthode setup pour créer l'environnement temporaire.
 4. Méthode teardown pour nettoyer.
 5. Méthode de test pour chaque catégorie.

 Cependant, nous allons écrire un test intégré qui simule le flux complet.

 Nous allons créer un test qui:
   - Configure le daemon avec un dossier source et des dossiers de destination.
   - Démarre le daemon.
   - Dépose un fichier dans le dossier source.
   - Vérifie que le fichier est déplacé.

 Nous allons utiliser la classe FileHandler et Classifier pour le test, mais dans le test d'intégration,
 nous testons l'ensemble du système, donc nous allons lancer le daemon qui utilise ces composants.

 Organiser le code:

 Nous allons créer un contexte temporaire en utilisant tempfile.mkdtemp.

 Pour le daemon, nous avons besoin de:
   - Un dossier source (à surveiller)
   - Un dossier de destination (qui contiendra les sous-dossiers de catégories)

 Nous allons créer ces dossiers dans le répertoire temporaire.

 Nous allons également créer un fichier config.json temporaire.

 Nous allons lancer le daemon dans un thread, mais nous devons pouvoir l'arrêter.

 Le daemon dans organizer.py a une boucle infinie, donc nous allons l'arrêter en utilisant un signal.

 Nous pouvons lancer le daemon avec un timeout, ou alors nous pouvons le concevoir pour qu'il puisse être arrêté par programme.

 Dans organizer.py, nous avons une boucle while True avec un time.sleep. Nous pouvons ajouter une condition d'arrêt.

 Pour les tests, nous allons modifier organizer.py pour qu'il puisse être arrêté par un événement de threading.

 Cependant, pour ne pas modifier le code principal pour les tests, nous allons plutôt utiliser un processus séparé et le tuer à la fin.

 Mais utiliser un processus rend les tests plus complexes et lents.

 Alternative: nous pouvons créer une classe de daemon qui peut être arrêtée, et dans les tests nous utilisons cette classe.

 Nous allons modifier organizer.py pour qu'il utilise un événement de threading pour la boucle principale.

 Mais comme nous devons générer le code de organizer.py, nous allons le faire avec cette capacité.

 Dans le code de organizer.py que nous avons généré, nous avons une boucle infinie. Nous allons la modifier pour qu'elle puisse être interrompue par un signal.

 Cependant, pour le test d'intégration, nous allons plutôt utiliser un script de test qui lance le daemon dans un sous-processus.

 Nous allons utiliser le module subprocess pour lancer organizer.py avec les arguments de configuration temporaire.

 Nous allons ensuite ajouter des fichiers, puis arrêter le sous-processus.

 C'est plus propre car cela simule vraiment l'exécution du daemon.

 Nous allons donc:

   - Créer un environnement temporaire.
   - Écrire un config.json temporaire.
   - Lancer organizer.py en tant que sous-processus.
   - Attendre un peu pour qu'il démarre.
   - Créer un fichier dans le dossier source.
   - Attendre un peu pour le traitement.
   - Vérifier le déplacement du fichier.
   - Tuer le sous-processus.

 Cela évite de modifier le code du daemon pour les tests.

 Nous allons donc utiliser subprocess.Popen.

 Code du test:

   import tempfile
   import os
   import json
   import time
   import subprocess
   import signal

   class TestIntegration(unittest.TestCase):

        def setUp(self):
            # Créer un répertoire temporaire
            self.test_dir = tempfile.mkdtemp()
            # Créer le dossier source (simulant Downloads)
            self.source_dir = os.path.join(self.test_dir, 'Downloads')
            os.makedirs(self.source_dir)
            # Créer le dossier de destination (simulant les dossiers organisés)
            self.dest_dir = os.path.join(self.test_dir, 'Organized')
            os.makedirs(self.dest_dir)

            # Créer les sous-dossiers de catégories dans le dossier de destination
            self.categories = ['Images', 'Videos', 'Documents', 'Archives', 'Code', 'Musique', 'Installeurs']
            for cat in self.categories:
                os.makedirs(os.path.join(self.dest_dir, cat))

            # Créer un fichier config.json temporaire
            self.config = {
                "source_dir": self.source_dir,
                "dest_dir": self.dest_dir,
                "rules": {
                    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
                    "Videos": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"],
                    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".doc", ".xls", ".ppt"],
                    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php"],
                    "Musique": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
                    "Installeurs": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"]
                },
                "log_file": os.path.join(self.test_dir, "organizer.log"),
                "web_interface": {
                    "host": "localhost",
                    "port": 8080,
                    "debug": False
                }
            }
            self.config_file = os.path.join(self.test_dir, 'config.json')
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)

            # Lancer le daemon en arrière-plan
            self.daemon_process = subprocess.Popen(['python', 'organizer.py', '--config', self.config_file])

            # Attendre un peu pour que le daemon démarre
            time.sleep(2)

        def tearDown(self):
            # Arrêter le daemon
            self.daemon_process.terminate()
            self.daemon_process.wait()
            # Supprimer le répertoire temporaire
            import shutil
            shutil.rmtree(self.test_dir)

        def test_image_file(self):
            # Créer un fichier image dans le dossier source
            test_file = os.path.join(self.source_dir, 'test_image.jpg')
            with open(test_file, 'wb') as f:
                f.write(b'fake image data')

            # Attendre que le daemon traite le fichier
            time.sleep(1)

            # Vérifier que le fichier a été déplacé dans le dossier Images
            expected_path = os.path.join(self.dest_dir, 'Images', 'test_image.jpg')
            self.assertTrue(os.path.exists(expected_path))
            self.assertFalse(os.path.exists(test_file))

        # On peut ajouter d'autres tests pour d'autres catégories

 Cependant, il y a un problème: le daemon organizer.py utilise le chemin du fichier de configuration par défaut (config.json) ou un argument.
 Nous devons donc modifier organizer.py pour accepter un argument en ligne de commande.

 Dans organizer.py, nous lisons config.json dans le répertoire courant. Nous allons le modifier pour accepter un argument.

 Nous allons donc supposer que organizer.py peut prendre un argument --config pour spécifier le fichier de configuration.

 Nous n'avons pas encore généré organizer.py, mais nous allons le faire avec cette fonctionnalité.

 Pour le test, nous allons lancer organizer.py avec le fichier de configuration temporaire.

 Mais attention, le daemon va écrire des logs dans le fichier config['log_file'].

 Nous allons donc vérifier aussi les logs.

 Cependant, pour ne pas alourdir, nous allons nous contenter de vérifier le déplacement.

 Nous allons écrire plusieurs tests pour chaque catégorie.

 Mais note: le test lance un sous-processus, ce qui est lent. Nous allons donc regrouper plusieurs tests dans une seule méthode.

 Nous allons plutôt écrire une méthode qui teste plusieurs catégories à la suite, pour éviter de redémarrer le daemon à chaque fois.

 Mais si nous faisons cela, il faut faire attention à ce que les fichiers ne se chevauchent pas.

 Nous allons donc:

   - Dans setUp, démarrer le daemon.
   - Dans tearDown, arrêter le daemon.
   - Écrire une méthode de test qui crée un fichier pour chaque catégorie et vérifie son déplacement.

 Cela réduit le nombre de démarrages du daemon.

 Nous allons donc:

        def test_multiple_categories(self):
            # Pour chaque catégorie, créer un fichier avec une extension correspondante
            test_cases = [
                ('test_image.jpg', 'Images'),
                ('test_video.mp4', 'Videos'),
                ('test_document.pdf', 'Documents'),
                ('test_archive.zip', 'Archives'),
                ('test_code.py', 'Code'),
                ('test_musique.mp3', 'Musique'),
                ('test_installeur.exe', 'Installeurs')
            ]

            for filename, expected_category in test_cases:
                with self.subTest(filename=filename, expected_category=expected_category):
                    source_path = os.path.join(self.source_dir, filename)
                    # Créer le fichier avec un contenu quelconque
                    with open(source_path, 'wb') as f:
                        f.write(b'fake content')

                    # Attendre un peu pour le traitement
                    time.sleep(0.5)

                    # Vérifier le déplacement
                    expected_path = os.path.join(self.dest_dir, expected_category, filename)
                    self.assertTrue(os.path.exists(expected_path), f"Le fichier {filename} n'a pas été déplacé vers {expected_category}")
                    self.assertFalse(os.path.exists(source_path), f"Le fichier {filename} existe toujours à la source")

                    # Si le fichier a été déplacé, on le supprime du dossier de destination pour le prochain test
                    # pour éviter qu'un fichier du même nom existe déjà (bien que dans notre cas les noms sont uniques)
                    # Mais attention: si on le supprime, on ne peut pas le réutiliser. Or on utilise des noms uniques, donc pas besoin.

            # Note: si on veut tester plusieurs fichiers dans la même catégorie, il faudrait le faire dans un test séparé.

 Cependant, il faut être prudent avec le timing. Nous pourrions manquer un fichier si le daemon n'a pas eu le temps de le traiter.

 Nous pouvons utiliser une attente active avec un timeout.

 Nous allons donc, pour chaque fichier, attendre jusqu'à 2 secondes qu'il soit déplacé.

 Nous allons écrire une fonction d'attente.

 Nous allons également vérifierimport unittest
import tempfile
import os
import json
import time
import subprocess
import shutil
import random
import urllib.request
import urllib.error
from threading import Thread
from http.server import HTTPServer
import sys

# Ajouter le répertoire parent au chemin pour importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web_interface import app


class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Créer un répertoire temporaire pour tous les tests
        cls.test_dir = tempfile.mkdtemp()
        
        # Créer les dossiers source et destination
        cls.source_dir = os.path.join(cls.test_dir, 'Downloads')
        os.makedirs(cls.source_dir)
        cls.dest_dir = os.path.join(cls.test_dir, 'Organized')
        os.makedirs(cls.dest_dir)
        
        # Créer les sous-dossiers de catégories
        categories = ['Images', 'Videos', 'Documents', 'Archives', 'Code', 'Musique', 'Installeurs']
        for cat in categories:
            os.makedirs(os.path.join(cls.dest_dir, cat))
        
        # Choisir un port aléatoire pour l'interface web
        cls.web_port = random.randint(8080, 9000)
        
        # Créer la configuration de test
        cls.config = {
            "source_dir": cls.source_dir,
            "dest_dir": cls.dest_dir,
            "rules": {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
                "Videos": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"],
                "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".doc", ".xls", ".ppt"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php"],
                "Musique": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
                "Installeurs": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"]
            },
            "log_file": os.path.join(cls.test_dir, "organizer.log"),
            "web_interface": {
                "host": "localhost",
                "port": cls.web_port,
                "debug": False
            }
        }
        
        # Écrire le fichier config.json temporaire
        cls.config_file = os.path.join(cls.test_dir, 'config.json')
        with open(cls.config_file, 'w') as f:
            json.dump(cls.config, f, indent=4)
    
    @classmethod
    def tearDownClass(cls):
        # Nettoyer le répertoire temporaire
        shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        # Lancer le daemon organizer.py en arrière-plan
        self.daemon_process = subprocess.Popen(
            [sys.executable, 'organizer.py', '--config', self.config_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Attendre que le daemon démarre
        time.sleep(2)
    
    def tearDown(self):
        # Arrêter le daemon
        self.daemon_process.terminate()
        self.daemon_process.wait()
        
        # Nettoyer tous les fichiers créés pendant le test
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        
        for category in os.listdir(self.dest_dir):
            category_path = os.path.join(self.dest_dir, category)
            if os.path.isdir(category_path):
                for file in os.listdir(category_path):
                    file_path = os.path.join(category_path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
    
    def wait_for_file(self, filepath, timeout=5, should_exist=True):
        """Attendre qu'un fichier apparaisse ou disparaisse"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(filepath) == should_exist:
                return True
            time.sleep(0.1)
        return False
    
    def test_image_file_classification(self):
        """Test de classification d'un fichier image"""
        # Créer un fichier image dans le dossier source
        test_file = os.path.join(self.source_dir, 'test_image.jpg')
        with open(test_file, 'wb') as f:
            f.write(b'fake image data')
        
        # Attendre que le fichier soit déplacé
        expected_path = os.path.join(self.dest_dir, 'Images', 'test_image.jpg')
        self.assertTrue(
            self.wait_for_file(expected_path, timeout=3, should_exist=True),
            "Le fichier image n'a pas été déplacé dans le dossier Images"
        )
        
        # Vérifier que le fichier a disparu du dossier source
        self.assertFalse(
            os.path.exists(test_file),
            "Le fichier image existe toujours dans le dossier source"
        )
    
    def test_video_file_classification(self):
        """Test de classification d'un fichier vidéo"""
        test_file = os.path.join(self.source_dir, 'test_video.mp4')
        with open(test_file, 'wb') as f:
            f.write(b'fake video data')
        
        expected_path = os.path.join(self.dest_dir, 'Videos', 'test_video.mp4')
        self.assertTrue(
            self.wait_for_file(expected_path, timeout=3, should_exist=True),
            "Le fichier vidéo n'a pas été déplacé dans le dossier Videos"
        )
        self.assertFalse(os.path.exists(test_file))
    
    def test_document_file_classification(self):
        """Test de classification d'un fichier document"""
        test_file = os.path.join(self.source_dir, 'test_document.pdf')
        with open(test_file, 'wb') as f:
            f.write(b'fake pdf data')
        
        expected_path = os.path.join(self.dest_dir, 'Documents', 'test_document.pdf')
        self.assertTrue(
            self.wait_for_file(expected_path, timeout=3, should_exist=True),
            "Le fichier document n'a pas été déplacé dans le dossier Documents"
        )
        self.assertFalse(os.path.exists(test_file))
    
    def test_archive_file_classification(self):
        """Test de classification d'un fichier archive"""
        test_file = os.path.join(self.source_dir, 'test_archive.zip')
        with open(test_file, 'wb') as f:
            f.write(b'fake zip data')
        
        expected_path = os.path.join(self.dest_dir, 'Archives', 'test_archive.zip')
        self.assertTrue(
            self.wait_for_file(expected_path, timeout=3, should_exist=True),
            "Le fichier archive n'a pas été déplacé dans le dossier Archives"
        )
        self.assertFalse(os.path.exists(test_file))
    
    def test_code_file_classification(self):
        """Test de classification d'un fichier code"""
        test_file = os.path.join(self.source_dir, 'test_code.py')
        with open(test_file, 'w') as f:
            f.write('print("Hello World")')
        
        expected_path = os.path.join(self.dest_dir, 'Code', 'test_code.py')
        self.assertTrue(
            self.wait_for_file(expected_path, timeout=3, should_exist=True),
            "Le fichier code n'a pas été déplacé dans le dossier Code"
        )
        self.assertFalse(os.path.exists(test_file))
    
    def test_music_file_classification(self):
        """Test de classification d'un fichier musique"""
        test_file = os.path.join(self.source_dir, 'test_music.mp3')
        with open(test_file, 'wb') as f:
            f.write(b'fake music data')
        
        expected_path = os.path.join(self.dest_dir, 'Musique', 'test_music.mp3')
        self.assertTrue(
            self.wait_for_file(expected_path, timeout=3, should_exist=True),
            "Le fichier musique n'a pas été déplacé dans le dossier Musique"
        )
        self.assertFalse(os.path.exists(test_file))
    
    def test_installer_file_classification(self):
        """Test de classification d'un fichier installeur"""
        test_file = os.path.join(self.source_dir, 'test_installer.exe')
        with open(test_file, 'wb') as f:
            f.write(b'fake installer data')
        
        expected_path = os.path.join(self.dest_dir, 'Installeurs', 'test_installer.exe')
        self.assertTrue(
            self.wait_for_file(expected_path, timeout=3, should_exist=True),
            "Le fichier installeur n'a pas été déplacé dans le dossier Installeurs"
        )
        self.assertFalse(os.path.exists(test_file))
    
    def test_web_interface(self):
        """Test de l'interface web"""
        # Attendre que le serveur web démarre
        time.sleep(2)
        
        # Essayer de se connecter à l'interface web
        url = f"http://localhost:{self.web_port}/"
        try:
            response = urllib.request.urlopen(url, timeout=5)
            self.assertEqual(response.getcode(), 200)
        except urllib.error.URLError as e:
            self.fail(f"L'interface web ne répond pas: {e}")
    
    def test_concurrent_file_processing(self):
        """Test du traitement de plusieurs fichiers simultanés"""
        files_to_create = [
            ('image1.png', 'Images'),
            ('image2.jpg', 'Images'),
            ('doc1.pdf', 'Documents'),
            ('doc2.docx', 'Documents'),
            ('video1.mp4', 'Videos'),
            ('code1.js', 'Code')
        ]
        
        # Créer tous les fichiers en même temps
        for filename, _ in files_to_create:
            filepath = os.path.join(self.source_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(b'fake content')
        
        # Attendre un peu plus longtemps pour le traitement
        time.sleep(3)
        
        # Vérifier que tous les fichiers ont été déplacés
        for filename, expected_category in files_to_create:
            expected_path = os.path.join(self.dest_dir, expected_category, filename)
            self.assertTrue(
                os.path.exists(expected_path),
                f"Le fichier {filename} n'a pas été déplacé vers {expected_category}"
            )
            source_path = os.path.join(self.source_dir, filename)
            self.assertFalse(
                os.path.exists(source_path),
                f"Le fichier {filename} existe toujours à la source"
            )
    
    def test_unknown_extension(self):
        """Test d'un fichier avec une extension non reconnue"""
        test_file = os.path.join(self.source_dir, 'test.unknown')
        with open(test_file, 'wb') as f:
            f.write(b'fake data')
        
        # Le fichier ne doit pas être déplacé
        time.sleep(2)
        
        # Il doit rester dans le dossier source
        self.assertTrue(
            os.path.exists(test_file),
            "Le fichier avec extension inconnue a été déplacé, mais il aurait dû rester"
        )
        
        # Vérifier qu'il n'est dans aucun dossier de catégorie
        for category in os.listdir(self.dest_dir):
            category_path = os.path.join(self.dest_dir, category)
            if os.path.isdir(category_path):
                self.assertFalse(
                    os.path.exists(os.path.join(category_path, 'test.unknown')),
                    f"Le fichier inconnu a été déplacé dans {category}"
                )

if __name__ == '__main__':
    unittest.main(verbosity=2)
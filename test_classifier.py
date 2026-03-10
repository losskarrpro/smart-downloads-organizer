```python
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Ajouter le chemin du projet pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.classifier import classify_file


class TestClassifier(unittest.TestCase):
    """Tests unitaires pour la logique de classification"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.test_config = {
            "rules": {
                "Images": ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "ico", "tiff"],
                "Videos": ["mp4", "avi", "mov", "mkv", "flv", "wmv", "webm", "mpeg", "mpg"],
                "Documents": ["pdf", "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx", "ppt", "pptx", "md"],
                "Archives": ["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "tgz"],
                "Code": ["py", "js", "html", "css", "java", "cpp", "c", "h", "php", "rb", "go", "rs", "ts"],
                "Musique": ["mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"],
                "Installeurs": ["exe", "msi", "dmg", "pkg", "deb", "rpm", "apk", "appimage"]
            },
            "other_category": "Other",
            "default_destination": "Downloads",
            "log_file": "logs/organizer.log",
            "web_port": 8080,
            "host": "localhost"
        }
    
    def test_classify_images(self):
        """Test classification des fichiers images"""
        test_cases = [
            ("photo.jpg", "Images"),
            ("image.jpeg", "Images"),
            ("screenshot.png", "Images"),
            ("animation.gif", "Images"),
            ("bitmap.bmp", "Images"),
            ("vector.svg", "Images"),
            ("photo.webp", "Images"),
            ("favicon.ico", "Images"),
            ("scan.tiff", "Images")
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_videos(self):
        """Test classification des fichiers vidéos"""
        test_cases = [
            ("movie.mp4", "Videos"),
            ("film.avi", "Videos"),
            ("video.mov", "Videos"),
            ("film.mkv", "Videos"),
            ("clip.flv", "Videos"),
            ("recording.wmv", "Videos"),
            ("video.webm", "Videos"),
            ("movie.mpeg", "Videos"),
            ("film.mpg", "Videos")
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_documents(self):
        """Test classification des documents"""
        test_cases = [
            ("document.pdf", "Documents"),
            ("doc.doc", "Documents"),
            ("document.docx", "Documents"),
            ("notes.txt", "Documents"),
            ("file.rtf", "Documents"),
            ("document.odt", "Documents"),
            ("spreadsheet.xls", "Documents"),
            ("spreadsheet.xlsx", "Documents"),
            ("presentation.ppt", "Documents"),
            ("presentation.pptx", "Documents"),
            ("readme.md", "Documents")
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_archives(self):
        """Test classification des archives"""
        test_cases = [
            ("archive.zip", "Archives"),
            ("archive.rar", "Archives"),
            ("archive.7z", "Archives"),
            ("archive.tar", "Archives"),
            ("compressed.gz", "Archives"),
            ("compressed.bz2", "Archives"),
            ("compressed.xz", "Archives"),
            ("archive.tgz", "Archives")
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_code(self):
        """Test classification des fichiers de code"""
        test_cases = [
            ("script.py", "Code"),
            ("script.js", "Code"),
            ("page.html", "Code"),
            ("style.css", "Code"),
            ("program.java", "Code"),
            ("program.cpp", "Code"),
            ("program.c", "Code"),
            ("header.h", "Code"),
            ("script.php", "Code"),
            ("script.rb", "Code"),
            ("program.go", "Code"),
            ("program.rs", "Code"),
            ("script.ts", "Code")
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_music(self):
        """Test classification des fichiers musicaux"""
        test_cases = [
            ("song.mp3", "Musique"),
            ("audio.wav", "Musique"),
            ("audio.flac", "Musique"),
            ("song.aac", "Musique"),
            ("audio.ogg", "Musique"),
            ("song.m4a", "Musique"),
            ("audio.wma", "Musique")
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_installers(self):
        """Test classification des installateurs"""
        test_cases = [
            ("setup.exe", "Installeurs"),
            ("installer.msi", "Installeurs"),
            ("installer.dmg", "Installeurs"),
            ("package.pkg", "Installeurs"),
            ("package.deb", "Installeurs"),
            ("package.rpm", "Installeurs"),
            ("app.apk", "Installeurs"),
            ("app.AppImage", "Installeurs")
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_unknown_extension(self):
        """Test classification avec extension inconnue"""
        test_cases = [
            ("file.unknown", "Other"),
            ("data.dat", "Other"),
            ("config.cfg", "Other"),
            ("", "Other"),  # Pas d'extension
            (".hidden", "Other"),  # Pas de nom de fichier
            ("noextension", "Other")  # Pas d'extension
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_case_insensitive(self):
        """Test classification insensible à la casse"""
        test_cases = [
            ("IMAGE.JPG", "Images"),
            ("Image.Jpeg", "Images"),
            ("VIDEO.MP4", "Videos"),
            ("Document.PDF", "Documents"),
            ("archive.ZIP", "Archives"),
            ("script.PY", "Code"),
            ("song.MP3", "Musique"),
            ("setup.EXE", "Installeurs")
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    deftest_classify_with_multiple_extensions(self):
        """Test classification avec extensions multiples"""
        test_cases = [
            ("archive.tar.gz", "Archives"),  # Double extension
            ("backup.tar.bz2", "Archives"),
            ("compressed.tar.xz", "Archives"),
            ("image.jpg.bak", "Other"),  # Dernière extension inconnue
            ("document.pdf.zip", "Archives"),  # PDF dans une archive
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_with_path(self):
        """Test classification avec chemin complet"""
        test_cases = [
            ("/home/user/Downloads/photo.jpg", "Images"),
            ("C:\\Users\\User\\Downloads\\document.pdf", "Documents"),
            ("../Downloads/video.mp4", "Videos"),
            ("./file.zip", "Archives"),
        ]
        
        for filepath, expected_category in test_cases:
            with self.subTest(filepath=filepath):
                category = classify_file(filepath, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_with_spaces_and_special_chars(self):
        """Test classification avec espaces et caractères spéciaux"""
        test_cases = [
            ("my photo.jpg", "Images"),
            ("document (1).pdf", "Documents"),
            ("video file.mp4", "Videos"),
            ("archive-file.zip", "Archives"),
            ("script_v1.0.py", "Code"),
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_with_empty_config(self):
        """Test classification avec configuration vide"""
        empty_config = {"rules": {}, "other_category": "Other"}
        
        test_cases = [
            ("photo.jpg", "Other"),
            ("document.pdf", "Other"),
            ("video.mp4", "Other"),
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, empty_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_missing_other_category(self):
        """Test classification sans catégorie 'Other' définie"""
        config_without_other = {
            "rules": {
                "Images": ["jpg", "png"],
                "Documents": ["pdf", "txt"]
            }
            # Pas de other_category
        }
        
        test_cases = [
            ("photo.jpg", "Images"),
            ("document.pdf", "Documents"),
            ("video.mp4", "Other"),  # Devrait retourner "Other" par défaut
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, config_without_other)
                self.assertEqual(category, expected_category)
    
    def test_classify_custom_other_category(self):
        """Test classification avec catégorie 'Other' personnalisée"""
        custom_config = {
            "rules": {
                "Images": ["jpg", "png"],
                "Documents": ["pdf", "txt"]
            },
            "other_category": "Divers"
        }
        
        test_cases = [
            ("photo.jpg", "Images"),
            ("document.pdf", "Documents"),
            ("video.mp4", "Divers"),
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                category = classify_file(filename, custom_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_invalid_input(self):
        """Test classification avec entrées invalides"""
        test_cases = [
            (None, "Other"),
            (123, "Other"),  # Nombre
            (["file.txt"], "Other"),  # Liste
            ({"name": "file.txt"}, "Other"),  # Dictionnaire
        ]
        
        for invalid_input, expected_category in test_cases:
            with self.subTest(input=invalid_input):
                category = classify_file(invalid_input, self.test_config)
                self.assertEqual(category, expected_category)
    
    def test_classify_overlapping_extensions(self):
        """Test classification avec extensions dans plusieurs catégories"""
        # Dans ce test, on vérifie que la première catégorie qui contient l'extension est utilisée
        overlapping_config = {
            "rules": {
                "Cat1": ["txt", "pdf"],
                "Cat2": ["pdf", "doc"],  # pdf est dans Cat1 et Cat2
            },
            "other_category": "Other"
        }
        
        # Le comportement attendu dépend de l'implémentation
        # On s'attend à ce que la première catégorie correspondante soit utilisée
        category = classify_file("document.pdf", overlapping_config)
        self.assertEqual(category, "Cat1")
    
    @patch('utils.classifier.CONFIG_FILE', 'non_existent.json')
    def test_classify_with_file_not_found(self):
        """Test classification quand le fichier de config n'existe pas"""
        # On teste que la fonction gère proprement l'absence de fichier config
        # En utilisant la configuration par défaut ou en levant une exception
        try:
            category = classify_file("test.jpg", {})
            # Si on arrive ici, on vérifie que c'est "Other" par défaut
            self.assertEqual(category, "Other")
        except Exception as e:
            # Ou on vérifie que l'exception est de type FileNotFoundError
            self.assertIsInstance(e, FileNotFoundError)

    def test_classify_performance(self):
        """Test de performance de la classification"""
        import time
        
        # Fichier avec extension connue
        start_time = time.time()
        for _ in range(1000):
            classify_file("performance_test.jpg", self.test_config)
        elapsed = time.time() - start_time
        
        # La classification devrait être rapide
        self.assertLess(elapsed, 1.0, "La classification est trop lente")


if __name__ == '__main__':
    # Créer une suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClassifier)
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Afficher un résumé
    print(f"\n{'='*60}")
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    
    if result.failures:
        print("\nÉchecs détaillés:")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
    
    if result.errors:
        print("\nErreurs détaillées:")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
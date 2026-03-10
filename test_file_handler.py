import unittest
import os
import shutil
import tempfile
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock
import hashlib

# Import the module to test
from utils.file_handler import (
    move_file,
    delete_file,
    get_file_info,
    calculate_hash,
    create_directory,
    copy_file,
    get_file_extension,
    is_file_locked,
    safe_filename,
    get_directory_size,
    get_file_count
)


class TestFileHandler(unittest.TestCase):
    """Test cases for file operations."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.source_file = os.path.join(self.test_dir, "test_source.txt")
        self.dest_file = os.path.join(self.test_dir, "test_dest.txt")
        
        # Create a test file with content
        with open(self.source_file, 'w') as f:
            f.write("Test content for file operations.")

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_move_file_success(self):
        """Test moving a file successfully."""
        result = move_file(self.source_file, self.dest_file)
        self.assertTrue(result)
        self.assertFalse(os.path.exists(self.source_file))
        self.assertTrue(os.path.exists(self.dest_file))
        
        # Verify content
        with open(self.dest_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Test content for file operations.")

    def test_move_file_source_not_found(self):
        """Test moving a non-existent file."""
        result = move_file("nonexistent.txt", self.dest_file)
        self.assertFalse(result)

    def test_move_file_destination_exists(self):
        """Test moving to an existing destination."""
        # Create destination file
        with open(self.dest_file, 'w') as f:
            f.write("Existing content.")
        
        result = move_file(self.source_file, self.dest_file)
        self.assertTrue(result)
        self.assertFalse(os.path.exists(self.source_file))
        
        # Verify destination was overwritten
        with open(self.dest_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Test content for file operations.")

    def test_move_file_permission_error(self):
        """Test moving file with permission error."""
        with patch('os.rename', side_effect=PermissionError("Permission denied")):
            result = move_file(self.source_file, self.dest_file)
            self.assertFalse(result)

    def test_delete_file_success(self):
        """Test deleting a file successfully."""
        result = delete_file(self.source_file)
        self.assertTrue(result)
        self.assertFalse(os.path.exists(self.source_file))

    def test_delete_file_not_found(self):
        """Test deleting a non-existent file."""
        result = delete_file("nonexistent.txt")
        self.assertFalse(result)

    def test_delete_file_permission_error(self):
        """Test deleting file with permission error."""
        with patch('os.remove', side_effect=PermissionError("Permission denied")):
            result = delete_file(self.source_file)
            self.assertFalse(result)

    def test_get_file_info(self):
        """Test getting file information."""
        info = get_file_info(self.source_file)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['filename'], "test_source.txt")
        self.assertEqual(info['extension'], ".txt")
        self.assertIn('size', info)
        self.assertIn('created', info)
        self.assertIn('modified', info)
        self.assertIn('accessed', info)
        self.assertGreater(info['size'], 0)
        
        # Check that dates are datetime objects
        self.assertIsInstance(info['created'], datetime)
        self.assertIsInstance(info['modified'], datetime)
        self.assertIsInstance(info['accessed'], datetime)

    def test_get_file_info_nonexistent(self):
        """Test getting info for non-existent file."""
        info = get_file_info("nonexistent.txt")
        self.assertIsNone(info)

    def test_calculate_hash_md5(self):
        """Test calculating MD5 hash of a file."""
        # Create file with known content
        test_content = b"Hello, World!"
        test_file = os.path.join(self.test_dir, "hash_test.txt")
        
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        expected_hash = hashlib.md5(test_content).hexdigest()
        result_hash = calculate_hash(test_file)
        
        self.assertEqual(result_hash, expected_hash)

    def test_calculate_hash_sha256(self):
        """Test calculating SHA256 hash of a file."""
        test_content = b"Hello, World!"
        test_file = os.path.join(self.test_dir, "hash_test.txt")
        
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        expected_hash = hashlib.sha256(test_content).hexdigest()
        result_hash = calculate_hash(test_file, algorithm='sha256')
        
        self.assertEqual(result_hash, expected_hash)

    def test_calculate_hash_nonexistent(self):
        """Test calculating hash for non-existent file."""
        result = calculate_hash("nonexistent.txt")
        self.assertIsNone(result)

    def test_create_directory(self):
        """Test creating a directory."""
        new_dir = os.path.join(self.test_dir, "new_folder")
        result = create_directory(new_dir)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))

    def test_create_directory_already_exists(self):
        """Test creating a directory that already exists."""
        result = create_directory(self.test_dir)
        self.assertTrue(result)  # Should return True even if exists

    def test_create_directory_permission_error(self):
        """Test creating directory with permission error."""
        with patch('os.makedirs', side_effect=PermissionError("Permission denied")):
            result = create_directory("/root/test_folder")
            self.assertFalse(result)

    def test_copy_file(self):
        """Test copying a file."""
        result = copy_file(self.source_file, self.dest_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.source_file))  # Source should still exist
        self.assertTrue(os.path.exists(self.dest_file))    # Destination should exist
        
        # Verify content
        with open(self.dest_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Test content for file operations.")

    def test_copy_file_nonexistent_source(self):
        """Test copying non-existent file."""
        result = copy_file("nonexistent.txt", self.dest_file)
        self.assertFalse(result)

    def test_get_file_extension(self):
        """Test getting file extension."""
        test_cases = [
            ("file.txt", ".txt"),
            ("archive.tar.gz", ".gz"),
            ("no_extension", ""),
            (".hidden", ""),
            ("file.with.multiple.dots.txt", ".txt"),
            ("/path/to/file.pdf", ".pdf"),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = get_file_extension(filename)
                self.assertEqual(result, expected)

    def test_is_file_locked(self):
        """Test checking if file is locked (in use)."""
        # On POSIX systems, we can test by trying to open the file
        result = is_file_locked(self.source_file)
        self.assertIsInstance(result, bool)

    @patch('os.path.exists', return_value=False)
    def test_is_file_locked_nonexistent(self, mock_exists):
        """Test checking lock on non-existent file."""
        result = is_file_locked("nonexistent.txt")
        self.assertFalse(result)

    def test_safe_filename(self):
        """Test creating safe filename."""
        test_cases = [
            ("file:name.txt", "file_name.txt"),
            ("file/with\\slashes.txt", "file_with_slashes.txt"),
            ("file*with?special<chars>.txt", "file_with_special_chars_.txt"),
            ("normal_file.txt", "normal_file.txt"),
            ("  spaced  .txt  ", "spaced.txt"),
            ("UPPERCASE.TXT", "UPPERCASE.TXT"),
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                result = safe_filename(original)
                self.assertEqual(result, expected)

    def test_get_directory_size(self):
        """Test getting directory size."""
        # Create additional files
        file1 = os.path.join(self.test_dir, "file1.txt")
        file2 = os.path.join(self.test_dir, "file2.txt")
        
        with open(file1, 'w') as f:
            f.write("x" * 100)  # 100 bytes
        
        with open(file2, 'w') as f:
            f.write("y" * 200)  # 200 bytes
        
        # Create a subdirectory
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        
        file3 = os.path.join(subdir, "file3.txt")
        with open(file3, 'w') as f:
            f.write("z" * 150)  # 150 bytes
        
        # Total should be: 100 + 200 + 150 = 450 bytes
        size = get_directory_size(self.test_dir)
        self.assertGreaterEqual(size, 450)

    def test_get_directory_size_nonexistent(self):
        """Test getting size of non-existent directory."""
        size = get_directory_size("/nonexistent/path")
        self.assertEqual(size, 0)

    def test_get_file_count(self):
        """Test counting files in directory."""
        # Create files and directories
        file1 = os.path.join(self.test_dir, "file1.txt")
        file2 = os.path.join(self.test_dir, "file2.txt")
        subdir = os.path.join(self.test_dir, "subdir")
        
        with open(file1, 'w'):
            pass
        with open(file2, 'w'):
            pass
        os.makedirs(subdir)
        
        # Create file in subdirectory
        file3 = os.path.join(subdir, "file3.txt")
        with open(file3, 'w'):
            pass
        
        # Count should be 3 files total (recursive)
        count_recursive = get_file_count(self.test_dir, recursive=True)
        self.assertEqual(count_recursive, 3)
        
        # Count should be 2 files in root only
        count_non_recursive = get_file_count(self.test_dir, recursive=False)
        self.assertEqual(count_non_recursive, 2)

    def test_get_file_count_nonexistent(self):
        """Test counting files in non-existent directory."""
        count = get_file_count("/nonexistent/path")
        self.assertEqual(count, 0)


if __name__ == '__main__':
    unittest.main()
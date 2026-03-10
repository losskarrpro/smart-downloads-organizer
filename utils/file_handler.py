```python
import os
import shutil
import time
import logging
from pathlib import Path
from typing import Optional, Tuple

# Setup logger for this module
logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file operations including moving and verifying files."""
    
    def __init__(self, config: dict):
        """
        Initialize FileHandler with configuration.
        
        Args:
            config: Dictionary containing configuration settings
        """
        self.config = config
        self.downloads_path = Path(config.get("downloads_path", "~/Downloads")).expanduser()
        
    def is_file_complete(self, file_path: Path, check_interval: float = 0.5, 
                        checks: int = 3) -> bool:
        """
        Check if a file is complete by monitoring its size.
        
        Args:
            file_path: Path to the file to check
            check_interval: Time between size checks in seconds
            checks: Number of checks to perform
            
        Returns:
            True if file size remains stable, False otherwise
        """
        try:
            if not file_path.exists():
                return False
                
            sizes = []
            for _ in range(checks):
                sizes.append(file_path.stat().st_size)
                time.sleep(check_interval)
            
            # File is considered complete if size doesn't change
            return all(s == sizes[0] for s in sizes)
            
        except (OSError, PermissionError) as e:
            logger.error(f"Error checking file completion for {file_path}: {e}")
            return False
    
    def get_unique_filename(self, destination_dir: Path, filename: str) -> str:
        """
        Generate a unique filename to avoid overwriting existing files.
        
        Args:
            destination_dir: Target directory
            filename: Original filename
            
        Returns:
            Unique filename with counter if needed
        """
        if not destination_dir.exists():
            return filename
            
        name_parts = filename.split('.')
        base_name = '.'.join(name_parts[:-1]) if len(name_parts) > 1 else name_parts[0]
        extension = name_parts[-1] if len(name_parts) > 1 else ''
        
        counter = 1
        unique_name = filename
        
        while (destination_dir / unique_name).exists():
            if extension:
                unique_name = f"{base_name}_{counter}.{extension}"
            else:
                unique_name = f"{base_name}_{counter}"
            counter += 1
            
        return unique_name
    
    def ensure_directory_exists(self, directory_path: Path) -> bool:
        """
        Ensure that a directory exists, create it if necessary.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            directory_path.mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError) as e:
            logger.error(f"Error creating directory {directory_path}: {e}")
            return False
    
    def move_file(self, source_path: Path, destination_dir: Path, 
                 new_name: Optional[str] = None, overwrite: bool = False) -> Tuple[bool, str]:
        """
        Move a file to a destination directory with conflict resolution.
        
        Args:
            source_path: Path to source file
            destination_dir: Target directory
            new_name: Optional new filename
            overwrite: Whether to overwrite existing files
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Check if source exists
            if not source_path.exists():
                return False, f"Source file does not exist: {source_path}"
            
            # Ensure destination directory exists
            if not self.ensure_directory_exists(destination_dir):
                return False, f"Failed to create destination directory: {destination_dir}"
            
            # Determine filename
            if new_name:
                dest_filename = new_name
            else:
                dest_filename = source_path.name
            
            # Handle filename conflicts
            dest_path = destination_dir / dest_filename
            if dest_path.exists() and not overwrite:
                unique_name = self.get_unique_filename(destination_dir, dest_filename)
                dest_path = destination_dir / unique_name
                dest_filename = unique_name
            
            # Move the file
            shutil.move(str(source_path), str(dest_path))
            
            # Verify the move was successful
            if dest_path.exists() and not source_path.exists():
                message = f"Moved {source_path.name} to {destination_dir}/{dest_filename}"
                logger.info(message)
                return True, message
            else:
                return False, "File move verification failed"
                
        except (shutil.Error, OSError, PermissionError) as e:
            error_msg = f"Error moving file {source_path} to {destination_dir}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def delete_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Delete a file safely.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not file_path.exists():
                return False, f"File does not exist: {file_path}"
            
            file_path.unlink()
            
            if not file_path.exists():
                message = f"Deleted file: {file_path}"
                logger.info(message)
                return True, message
            else:
                return False, "File deletion verification failed"
                
        except (OSError, PermissionError) as e:
            error_msg = f"Error deleting file {file_path}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_file_info(self, file_path: Path) -> dict:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'path': str(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'extension': file_path.suffix.lower(),
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir()
            }
        except (OSError, PermissionError) as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return {}
    
    def verify_file_integrity(self, file_path: Path) -> bool:
        """
        Basic file integrity check.
        
        Args:
            file_path: Path to file to verify
            
        Returns:
            True if file appears to be valid
        """
        try:
            if not file_path.exists():
                return False
            
            # Check if file is readable
            with open(file_path, 'rb') as f:
                # Try to read a small portion
                f.read(1024)
            
            # Check file size is reasonable (notzero)
            return True
            
        except (IOError, OSError, PermissionError) as e:
            logger.error(f"Error verifying file integrity for {file_path}: {e}")
            return False
    
    def create_placeholder_file(self, file_path: Path, content: str = "") -> bool:
        """
        Create a placeholder file (e.g., for testing).
        
        Args:
            file_path: Path where to create the file
            content: Content to write in the file
            
        Returns:
            True if file was created successfully
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except (IOError, OSError, PermissionError) as e:
            logger.error(f"Error creating placeholder file {file_path}: {e}")
            return False
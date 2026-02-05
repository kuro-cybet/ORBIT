"""
ORBIT Secure File Operations Module

Provides secure file I/O with validation, locking, and atomic operations.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Any, Optional, List
from contextlib import contextmanager
from error_handler import get_error_handler, FileOperationException
from utils.validators import InputValidator

class SecureFileHandler:
    """Secure file operations with validation and atomic writes"""
    
    # File size limits (in bytes)
    MAX_JSON_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_LOG_SIZE = 50 * 1024 * 1024   # 50 MB
    MAX_TEXT_SIZE = 5 * 1024 * 1024   # 5 MB
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        '.json', '.txt', '.log', '.csv', '.md'
    }
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize secure file handler
        
        Args:
            base_dir: Base directory for file operations (optional)
        """
        self.error_handler = get_error_handler()
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_path(self, filepath: Path) -> Path:
        """
        Validate file path is safe
        
        Args:
            filepath: Path to validate
            
        Returns:
            Validated path
            
        Raises:
            FileOperationException: If path is invalid
        """
        try:
            # Sanitize path
            clean_path = InputValidator.sanitize_path(
                str(filepath),
                allowed_base_dirs=[self.base_dir]
            )
            
            # Check extension
            if clean_path.suffix not in self.ALLOWED_EXTENSIONS:
                raise FileOperationException(
                    f"File extension {clean_path.suffix} not allowed"
                )
            
            return clean_path
            
        except Exception as e:
            raise FileOperationException(f"Path validation failed: {e}")
    
    def _check_file_size(self, filepath: Path, max_size: int):
        """
        Check file size is within limits
        
        Args:
            filepath: File to check
            max_size: Maximum allowed size in bytes
            
        Raises:
            FileOperationException: If file is too large
        """
        if filepath.exists():
            size = filepath.stat().st_size
            if size > max_size:
                raise FileOperationException(
                    f"File size ({size} bytes) exceeds limit ({max_size} bytes)"
                )
    
    def read_json(self, filepath: Path) -> dict:
        """
        Safely read JSON file
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileOperationException: If read fails
        """
        try:
            clean_path = self._validate_path(filepath)
            self._check_file_size(clean_path, self.MAX_JSON_SIZE)
            
            if not clean_path.exists():
                raise FileOperationException(f"File not found: {clean_path}")
            
            with open(clean_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.error_handler.log_info(f"Successfully read JSON: {clean_path}")
            return data
            
        except json.JSONDecodeError as e:
            raise FileOperationException(f"Invalid JSON format: {e}")
        except Exception as e:
            raise FileOperationException(f"Failed to read JSON: {e}")
    
    def write_json(self, filepath: Path, data: Any, atomic: bool = True):
        """
        Safely write JSON file with atomic operation
        
        Args:
            filepath: Path to JSON file
            data: Data to write
            atomic: Use atomic write (write to temp then rename)
            
        Raises:
            FileOperationException: If write fails
        """
        try:
            clean_path = self._validate_path(filepath)
            
            # Serialize to JSON
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Check size
            if len(json_str.encode('utf-8')) > self.MAX_JSON_SIZE:
                raise FileOperationException("JSON data exceeds size limit")
            
            if atomic:
                # Atomic write: write to temp file then rename
                temp_fd, temp_path = tempfile.mkstemp(
                    dir=clean_path.parent,
                    suffix='.tmp'
                )
                
                try:
                    with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                        f.write(json_str)
                        f.flush()
                        os.fsync(f.fileno())
                    
                    # Atomic rename
                    shutil.move(temp_path, clean_path)
                    
                except Exception:
                    # Clean up temp file on error
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    raise
            else:
                # Direct write
                with open(clean_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
            
            # Set secure permissions (owner read/write only)
            os.chmod(clean_path, 0o600)
            
            self.error_handler.log_info(f"Successfully wrote JSON: {clean_path}")
            
        except Exception as e:
            raise FileOperationException(f"Failed to write JSON: {e}")
    
    def read_text(self, filepath: Path) -> str:
        """
        Safely read text file
        
        Args:
            filepath: Path to text file
            
        Returns:
            File contents
            
        Raises:
            FileOperationException: If read fails
        """
        try:
            clean_path = self._validate_path(filepath)
            self._check_file_size(clean_path, self.MAX_TEXT_SIZE)
            
            if not clean_path.exists():
                raise FileOperationException(f"File not found: {clean_path}")
            
            with open(clean_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            raise FileOperationException(f"Failed to read text file: {e}")
    
    def write_text(self, filepath: Path, content: str):
        """
        Safely write text file
        
        Args:
            filepath: Path to text file
            content: Content to write
            
        Raises:
            FileOperationException: If write fails
        """
        try:
            clean_path = self._validate_path(filepath)
            
            # Check size
            if len(content.encode('utf-8')) > self.MAX_TEXT_SIZE:
                raise FileOperationException("Text content exceeds size limit")
            
            with open(clean_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            os.chmod(clean_path, 0o600)
            
        except Exception as e:
            raise FileOperationException(f"Failed to write text file: {e}")
    
    def safe_delete(self, filepath: Path):
        """
        Safely delete file
        
        Args:
            filepath: Path to file to delete
            
        Raises:
            FileOperationException: If delete fails
        """
        try:
            clean_path = self._validate_path(filepath)
            
            if clean_path.exists():
                clean_path.unlink()
                self.error_handler.log_info(f"Deleted file: {clean_path}")
            
        except Exception as e:
            raise FileOperationException(f"Failed to delete file: {e}")
    
    def ensure_directory(self, dirpath: Path):
        """
        Safely create directory if it doesn't exist
        
        Args:
            dirpath: Directory path to create
            
        Raises:
            FileOperationException: If creation fails
        """
        try:
            # Validate directory is within base_dir
            clean_path = InputValidator.sanitize_path(
                str(dirpath),
                allowed_base_dirs=[self.base_dir]
            )
            
            clean_path.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            raise FileOperationException(f"Failed to create directory: {e}")
    
    @contextmanager
    def file_lock(self, filepath: Path):
        """
        Context manager for file locking
        
        Args:
            filepath: File to lock
            
        Yields:
            File path
        """
        lock_file = filepath.with_suffix(filepath.suffix + '.lock')
        
        try:
            # Create lock file
            lock_file.touch()
            yield filepath
        finally:
            # Remove lock file
            if lock_file.exists():
                lock_file.unlink()

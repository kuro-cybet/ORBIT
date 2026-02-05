"""
ORBIT Input Validation Module

Provides comprehensive input validation and sanitization.
"""

import re
import ipaddress
from pathlib import Path
from typing import Optional, List
from error_handler import get_error_handler, SecurityException

class InputValidator:
    """Input validation and sanitization utilities"""
    
    # Regex patterns
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_.-]+$')
    
    # Dangerous patterns
    SQL_INJECTION_PATTERNS = [
        r"('|(\\')|(;)|(--)|(\/\*)|(\\*\/))",
        r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\.",
        r"~",
        r"\/\/",
        r"\\\\",
    ]
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """
        Sanitize string input
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            SecurityException: If input contains dangerous patterns
        """
        if not isinstance(value, str):
            raise SecurityException("Input must be a string")
        
        # Check length
        if len(value) > max_length:
            raise SecurityException(f"Input exceeds maximum length of {max_length}")
        
        # Check for SQL injection patterns
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityException("Input contains potentially dangerous SQL patterns")
        
        # Strip whitespace
        return value.strip()
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not username or len(username) < 3 or len(username) > 32:
            return False
        
        return bool(InputValidator.ALPHANUMERIC_PATTERN.match(username))
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) > 128:
            return False, "Password is too long"
        
        # Check for at least one letter and one number
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        
        if not (has_letter and has_number):
            return False, "Password must contain letters and numbers"
        
        return True, ""
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        Validate filename is safe
        
        Args:
            filename: Filename to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not filename or len(filename) > 255:
            return False
        
        # Check for path traversal
        for pattern in InputValidator.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, filename):
                return False
        
        return bool(InputValidator.FILENAME_PATTERN.match(filename))
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """
        Validate IP address format
        
        Args:
            ip: IP address to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """
        Validate port number
        
        Args:
            port: Port number to validate
            
        Returns:
            True if valid, False otherwise
        """
        return isinstance(port, int) and 1 <= port <= 65535
    
    @staticmethod
    def validate_numeric_range(value: float, min_val: float, max_val: float) -> bool:
        """
        Validate numeric value is within range
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            True if valid, False otherwise
        """
        try:
            num = float(value)
            return min_val <= num <= max_val
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def sanitize_path(path: str, allowed_base_dirs: Optional[List[Path]] = None) -> Path:
        """
        Sanitize and validate file path
        
        Args:
            path: Path to sanitize
            allowed_base_dirs: List of allowed base directories
            
        Returns:
            Sanitized Path object
            
        Raises:
            SecurityException: If path is invalid or outside allowed directories
        """
        try:
            # Convert to Path and resolve
            clean_path = Path(path).resolve()
            
            # Check for path traversal
            if ".." in str(path):
                raise SecurityException("Path traversal detected")
            
            # If allowed directories specified, verify path is within them
            if allowed_base_dirs:
                is_allowed = any(
                    str(clean_path).startswith(str(base_dir.resolve()))
                    for base_dir in allowed_base_dirs
                )
                
                if not is_allowed:
                    raise SecurityException("Path is outside allowed directories")
            
            return clean_path
            
        except Exception as e:
            raise SecurityException(f"Invalid path: {e}")

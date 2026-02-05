"""
ORBIT Security Configuration Module

Provides secure credential management, encryption, and authentication utilities.
"""

import os
import json
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta

# Security constants
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
SESSION_TIMEOUT_MINUTES = 30
MIN_PASSWORD_LENGTH = 8

class SecurityConfig:
    """Centralized security configuration and credential management"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        self.credentials_file = self.config_dir / ".credentials"
        self.session_file = self.config_dir / ".session"
        self.login_attempts_file = self.config_dir / ".login_attempts"
        
        # Initialize default credentials if not exists
        self._initialize_credentials()
    
    def _initialize_credentials(self):
        """Initialize default credentials with secure hashing"""
        if not self.credentials_file.exists():
            default_users = {
                "admin": self._hash_password("orbit2026"),
                "user": self._hash_password("demo123")
            }
            self._save_credentials(default_users)
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password using SHA-256 with salt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password with salt
        """
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password to verify
            hashed: Stored hash with salt
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            salt, pwd_hash = hashed.split('$')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return test_hash == pwd_hash
        except Exception:
            return False
    
    def _save_credentials(self, credentials: Dict[str, str]):
        """Save credentials to secure file"""
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f)
            # Set file permissions (read/write for owner only)
            os.chmod(self.credentials_file, 0o600)
        except Exception as e:
            print(f"[Security] Error saving credentials: {e}")
    
    def _load_credentials(self) -> Dict[str, str]:
        """Load credentials from secure file"""
        try:
            if self.credentials_file.exists():
                with open(self.credentials_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[Security] Error loading credentials: {e}")
        return {}
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """
        Verify user credentials with rate limiting
        
        Args:
            username: Username to verify
            password: Password to verify
            
        Returns:
            True if credentials are valid and not locked out
        """
        # Check if account is locked
        if self._is_locked_out(username):
            return False
        
        # Load credentials
        credentials = self._load_credentials()
        
        if username not in credentials:
            self._record_failed_attempt(username)
            return False
        
        # Verify password
        if self._verify_password(password, credentials[username]):
            self._clear_failed_attempts(username)
            return True
        else:
            self._record_failed_attempt(username)
            return False
    
    def _is_locked_out(self, username: str) -> bool:
        """Check if account is locked due to failed attempts"""
        try:
            if not self.login_attempts_file.exists():
                return False
            
            with open(self.login_attempts_file, 'r') as f:
                attempts = json.load(f)
            
            if username not in attempts:
                return False
            
            user_attempts = attempts[username]
            
            # Check if locked out
            if user_attempts['count'] >= MAX_LOGIN_ATTEMPTS:
                lockout_time = datetime.fromisoformat(user_attempts['last_attempt'])
                unlock_time = lockout_time + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                
                if datetime.now() < unlock_time:
                    return True
                else:
                    # Lockout expired, clear attempts
                    self._clear_failed_attempts(username)
                    return False
            
            return False
        except Exception as e:
            print(f"[Security] Error checking lockout: {e}")
            return False
    
    def _record_failed_attempt(self, username: str):
        """Record a failed login attempt"""
        try:
            attempts = {}
            if self.login_attempts_file.exists():
                with open(self.login_attempts_file, 'r') as f:
                    attempts = json.load(f)
            
            if username not in attempts:
                attempts[username] = {'count': 0, 'last_attempt': None}
            
            attempts[username]['count'] += 1
            attempts[username]['last_attempt'] = datetime.now().isoformat()
            
            with open(self.login_attempts_file, 'w') as f:
                json.dump(attempts, f)
            
            os.chmod(self.login_attempts_file, 0o600)
        except Exception as e:
            print(f"[Security] Error recording failed attempt: {e}")
    
    def _clear_failed_attempts(self, username: str):
        """Clear failed login attempts for user"""
        try:
            if not self.login_attempts_file.exists():
                return
            
            with open(self.login_attempts_file, 'r') as f:
                attempts = json.load(f)
            
            if username in attempts:
                del attempts[username]
            
            with open(self.login_attempts_file, 'w') as f:
                json.dump(attempts, f)
        except Exception as e:
            print(f"[Security] Error clearing attempts: {e}")
    
    def get_remaining_attempts(self, username: str) -> int:
        """Get remaining login attempts before lockout"""
        try:
            if not self.login_attempts_file.exists():
                return MAX_LOGIN_ATTEMPTS
            
            with open(self.login_attempts_file, 'r') as f:
                attempts = json.load(f)
            
            if username not in attempts:
                return MAX_LOGIN_ATTEMPTS
            
            return max(0, MAX_LOGIN_ATTEMPTS - attempts[username]['count'])
        except Exception:
            return MAX_LOGIN_ATTEMPTS
    
    def create_session(self, username: str) -> str:
        """Create a secure session token"""
        token = secrets.token_urlsafe(32)
        session_data = {
            'username': username,
            'token': token,
            'created': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)).isoformat()
        }
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            os.chmod(self.session_file, 0o600)
        except Exception as e:
            print(f"[Security] Error creating session: {e}")
        
        return token
    
    def validate_session(self, token: str) -> bool:
        """Validate session token"""
        try:
            if not self.session_file.exists():
                return False
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            if session_data['token'] != token:
                return False
            
            expires = datetime.fromisoformat(session_data['expires'])
            if datetime.now() > expires:
                return False
            
            return True
        except Exception as e:
            print(f"[Security] Error validating session: {e}")
            return False
    
    def destroy_session(self):
        """Destroy current session"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
        except Exception as e:
            print(f"[Security] Error destroying session: {e}")

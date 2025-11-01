import sqlite3
import hashlib
import secrets
from datetime import datetime
import json
import os
from typing import Optional, Dict, Any

class AuthSystem:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                license_key TEXT UNIQUE,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        ''')
        conn.commit()
        conn.close()

    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with PBKDF2 and salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return salt, pw_hash.hex()

    def register_user(self, username: str, email: str, password: str, license_key: str) -> bool:
        """Register a new user with license key validation"""
        # Validate license key first
        if not self.validate_license(license_key):
            return False

        salt, password_hash = self.hash_password(password)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, license_key)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, license_key))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username, email, or license already exists
        finally:
            conn.close()

    def verify_login(self, username: str, password: str) -> bool:
        """Verify user login credentials"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT password_hash, salt FROM users
            WHERE (username = ? OR email = ?) AND is_active = 1
        ''', (username, username))

        result = cursor.fetchone()
        conn.close()

        if result:
            stored_hash, salt = result
            _, input_hash = self.hash_password(password, salt)
            if stored_hash == input_hash:
                # Update last login
                self._update_last_login(username)
                return True
        return False

    def _update_last_login(self, username: str):
        """Update user's last login timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET last_login = ? WHERE username = ? OR email = ?
        ''', (datetime.now(), username, username))
        conn.commit()
        conn.close()

    def validate_license(self, license_key: str) -> bool:
        """Validate if license key exists and is not used"""
        if not license_key or license_key.strip() == "":
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id FROM users
            WHERE license_key = ? AND is_active = 1
        ''', (license_key.strip(),))

        result = cursor.fetchone()
        conn.close()
        return result is None  # License is valid if not already used

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information for dashboard display"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT username, email, license_key, created_at, last_login
            FROM users
            WHERE (username = ? OR email = ?) AND is_active = 1
        ''', (username, username))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'username': result[0],
                'email': result[1],
                'license_key': result[2],
                'created_at': result[3],
                'last_login': result[4]
            }
        return None

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        if not self.verify_login(username, old_password):
            return False

        salt, password_hash = self.hash_password(new_password)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE users SET password_hash = ?, salt = ? WHERE username = ? OR email = ?
        ''', (password_hash, salt, username, username))

        conn.commit()
        conn.close()
        return True

    def deactivate_user(self, username: str) -> bool:
        """Deactivate user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE users SET is_active = 0 WHERE username = ? OR email = ?
        ''', (username, username))

        conn.commit()
        conn.close()
        return True

    def get_user_count(self) -> int:
        """Get total number of registered users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else 0

    def cleanup_expired_sessions(self):
        """Clean up any expired session data (placeholder for future use)"""
        # This could be expanded for session management
        pass

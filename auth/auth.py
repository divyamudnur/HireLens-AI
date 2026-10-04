import hashlib
import os
import sqlite3
from database.database import get_connection
from auth.roles import logout_session

def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2 with SHA-256 and a random salt."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + '$' + key.hex()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a plain password against the stored salt$hash string."""
    try:
        salt_hex, key_hex = stored_hash.split('$')
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return new_key == key
    except Exception:
        return False

def register_user(name: str, email: str, password: str, role: str) -> tuple[bool, str]:
    """
    Registers a new user in the database.
    Validates required fields, duplicate emails, and role values.
    Returns (success: bool, message: str)
    """
    name = name.strip() if name else ""
    email = email.strip().lower() if email else ""
    role = role.lower().strip() if role else ""

    if not name or not email or not password:
        return False, "All fields (name, email, password) are required."
    
    if role not in ('candidate', 'employer'):
        return False, "Invalid user role selected. Must be Candidate or Employer."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    hashed_pw = hash_password(password)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hashed_pw, role)
        )
        conn.commit()
        return True, "Registration successful! You can now log in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"
    finally:
        conn.close()

def login_user(email: str, password: str) -> tuple[dict | None, str]:
    """
    Authenticates a user with email and password.
    Returns (user_dict or None, message: str)
    """
    email = email.strip().lower() if email else ""
    if not email or not password:
        return None, "Please enter both email and password."

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password, role, created_at FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user is None:
            return None, "Invalid email or password."

        if verify_password(password, user['password']):
            user_data = {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role'],
                "created_at": user['created_at']
            }
            return user_data, "Login successful!"
        else:
            return None, "Invalid email or password."

    except Exception as e:
        return None, f"Login failed: {str(e)}"
    finally:
        conn.close()

def logout_user():
    """Logs out current user by clearing session state."""
    logout_session()


import sqlite3
import hashlib
import hmac
import os
from getpass import getpass

DB_NAME = "task_management.db"


# 1. DATABASE CONNECTION
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# 2. CREATE DATABASE TABLES
def create_tables():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS Tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                deadline TEXT,
                priority TEXT NOT NULL DEFAULT 'Medium'
                    CHECK (priority IN ('Low', 'Medium', 'High')),
                status TEXT NOT NULL DEFAULT 'Pending'
                    CHECK (status IN ('Pending', 'In Progress', 'Completed')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
                    ON DELETE CASCADE
            )
        """)


# 3. PASSWORD HASHING
def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 200000
    )
    return salt.hex() + "$" + digest.hex()


def verify_password(password, stored_hash):
    try:
        salt_hex, expected_hash = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, AttributeError):
        return False

    actual_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 200000
    ).hex()

    return hmac.compare_digest(actual_hash, expected_hash)


def read_password(prompt="Password: "):
    try:
        return getpass(prompt)
    except (EOFError, KeyboardInterrupt):
        raise


# 4. USER REGISTRATION
def register():
    print("\n--- User Registration ---")

    name = input("Enter your name: ").strip()
    email = input("Enter your email: ").strip().lower()
    password = read_password("Create a password (minimum 6 characters): ")

    if not name or not email or not password:
        print("All fields are required.")
        return

    if "@" not in email or "." not in email.split("@")[-1]:
        print("Enter a valid email address.")
        return

    if len(password) < 6:
        print("Password must contain at least 6 characters.")
        return

    try:
        with connect_db() as conn:
            conn.execute("""
                INSERT INTO Users (name, email, password_hash)
                VALUES (?, ?, ?)
            """, (name, email, hash_password(password)))

        print("Registration successful! You can now log in.")

    except sqlite3.IntegrityError:
        print("An account with this email already exists.")


# 5. USER LOGIN
def login():
    print("\n--- User Login ---")

    email = input("Enter your email: ").strip().lower()
    password = read_password("Enter your password: ")

    with connect_db() as conn:
        user = conn.execute("""
            SELECT user_id, name, password_hash
            FROM Users
            WHERE email = ?
        """, (email,)).fetchone()

    if user and verify_password(password, user[2]):
        print(f"\nLogin successful! Welcome, {user[1]}.")
        return {"user_id": user[0], "name": user[1]}

    print("Invalid email or password.")
    return None


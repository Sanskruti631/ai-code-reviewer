import sqlite3
import hashlib
import secrets
from datetime import datetime

# Initialize the database
def init_db():
    conn = sqlite3.connect('code_reviewer.db')
    c = conn.cursor()
    
    # Users table with salt for password hashing
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Reviews table with user association
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            feedback TEXT NOT NULL,
            language TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# Password hashing utilities
def generate_salt():
    return secrets.token_hex(16)

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

# User registration
def register_user(username, password):
    conn = sqlite3.connect('code_reviewer.db')
    c = conn.cursor()
    try:
        salt = generate_salt()
        hashed_pw = hash_password(password, salt)
        c.execute("INSERT INTO users (username, salt, hashed_password) VALUES (?, ?, ?)", 
                 (username, salt, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username exists
    finally:
        conn.close()

# User login
def verify_user(username, password):
    conn = sqlite3.connect('code_reviewer.db')
    c = conn.cursor()
    c.execute("SELECT id, salt, hashed_password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user:
        user_id, salt, stored_hash = user
        if hash_password(password, salt) == stored_hash:
            return user_id
    return None

# Review management
def save_review(user_id, code, feedback, language):
    conn = sqlite3.connect('code_reviewer.db')
    c = conn.cursor()
    c.execute("INSERT INTO reviews (user_id, code, feedback, language) VALUES (?, ?, ?, ?)",
             (user_id, code[:5000], feedback[:5000], language))
    conn.commit()
    conn.close()

def get_user_reviews(user_id, limit=5):
    conn = sqlite3.connect('code_reviewer.db')
    c = conn.cursor()
    c.execute("""
        SELECT code, feedback, language, timestamp 
        FROM reviews 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (user_id, limit))
    reviews = [
        {
            "code": row[0],
            "feedback": row[1],
            "language": row[2],
            "timestamp": row[3]
        } for row in c.fetchall()
    ]
    conn.close()
    return reviews

# Initialize on import
init_db()

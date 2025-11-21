"""
PostgreSQL Migration Script
Migrates data from SQLite to PostgreSQL database
"""

import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import pool
import json
from datetime import datetime
from config import settings


def get_sqlite_connection():
    """Get SQLite database connection"""
    return sqlite3.connect("lexi.db")


def get_postgresql_connection():
    """Get PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Could not connect to PostgreSQL: {e}")
        return None


def create_postgresql_schema(pg_conn):
    """Create PostgreSQL schema (tables)"""
    cursor = pg_conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT,
            preferences TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create lessons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            lesson_type TEXT,
            difficulty_level TEXT,
            completed BOOLEAN DEFAULT FALSE,
            score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            lesson_id INTEGER,
            accuracy REAL,
            speed REAL,
            errors TEXT,
            session_duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (id)
        )
    ''')
    
    # Create chat_sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            session_id TEXT UNIQUE,
            messages TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create error_corrections table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS error_corrections (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            original_text TEXT,
            corrected_text TEXT,
            error_types TEXT,
            confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create dyslexia_tests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dyslexia_tests (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            test_type TEXT,
            answers TEXT,
            score REAL,
            risk_level TEXT,
            recommendations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create password_reset_tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    pg_conn.commit()
    print("✅ PostgreSQL schema created successfully")


def migrate_users(sl_conn, pg_conn):
    """Migrate users from SQLite to PostgreSQL"""
    sl_cursor = sl_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sl_cursor.execute('SELECT * FROM users')
    users = sl_cursor.fetchall()
    
    if not users:
        print("No users to migrate")
        return 0
    
    migrated = 0
    for user in users:
        try:
            pg_cursor.execute('''
                INSERT INTO users (id, email, username, hashed_password, full_name, preferences, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            ''', user)
            migrated += 1
        except Exception as e:
            print(f"Error migrating user {user[0]}: {e}")
    
    pg_conn.commit()
    print(f"✅ Migrated {migrated} users")
    return migrated


def migrate_lessons(sl_conn, pg_conn):
    """Migrate lessons from SQLite to PostgreSQL"""
    sl_cursor = sl_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sl_cursor.execute('SELECT * FROM lessons')
    lessons = sl_cursor.fetchall()
    
    if not lessons:
        print("No lessons to migrate")
        return 0
    
    migrated = 0
    for lesson in lessons:
        try:
            pg_cursor.execute('''
                INSERT INTO lessons (id, user_id, title, content, lesson_type, difficulty_level, completed, score, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            ''', lesson)
            migrated += 1
        except Exception as e:
            print(f"Error migrating lesson {lesson[0]}: {e}")
    
    pg_conn.commit()
    print(f"✅ Migrated {migrated} lessons")
    return migrated


def migrate_progress(sl_conn, pg_conn):
    """Migrate progress entries from SQLite to PostgreSQL"""
    sl_cursor = sl_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sl_cursor.execute('SELECT * FROM progress')
    progress_entries = sl_cursor.fetchall()
    
    if not progress_entries:
        print("No progress entries to migrate")
        return 0
    
    migrated = 0
    for entry in progress_entries:
        try:
            pg_cursor.execute('''
                INSERT INTO progress (id, user_id, lesson_id, accuracy, speed, errors, session_duration, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            ''', entry)
            migrated += 1
        except Exception as e:
            print(f"Error migrating progress entry {entry[0]}: {e}")
    
    pg_conn.commit()
    print(f"✅ Migrated {migrated} progress entries")
    return migrated


def migrate_dyslexia_tests(sl_conn, pg_conn):
    """Migrate dyslexia tests from SQLite to PostgreSQL"""
    sl_cursor = sl_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sl_cursor.execute('SELECT * FROM dyslexia_tests')
    tests = sl_cursor.fetchall()
    
    if not tests:
        print("No dyslexia tests to migrate")
        return 0
    
    migrated = 0
    for test in tests:
        try:
            pg_cursor.execute('''
                INSERT INTO dyslexia_tests (id, user_id, test_type, answers, score, risk_level, recommendations, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            ''', test)
            migrated += 1
        except Exception as e:
            print(f"Error migrating test {test[0]}: {e}")
    
    pg_conn.commit()
    print(f"✅ Migrated {migrated} dyslexia tests")
    return migrated


def reset_sequences(pg_conn):
    """Reset PostgreSQL sequences to prevent ID conflicts"""
    cursor = pg_conn.cursor()
    
    cursor.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))")
    cursor.execute("SELECT setval('lessons_id_seq', (SELECT MAX(id) FROM lessons))")
    cursor.execute("SELECT setval('progress_id_seq', (SELECT MAX(id) FROM progress))")
    cursor.execute("SELECT setval('dyslexia_tests_id_seq', (SELECT MAX(id) FROM dyslexia_tests))")
    
    pg_conn.commit()
    print("✅ PostgreSQL sequences reset")


def main():
    """Main migration function"""
    print("🚀 Starting PostgreSQL migration...")
    
    # Get connections
    sl_conn = get_sqlite_connection()
    pg_conn = get_postgresql_connection()
    
    if not pg_conn:
        print("❌ Failed to connect to PostgreSQL")
        print("\nPlease ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. Update config.py with your PostgreSQL credentials")
        print("3. Create the database: createdb lexilearn")
        return
    
    print("✅ Connected to both databases")
    
    # Create schema
    create_postgresql_schema(pg_conn)
    
    # Migrate data
    total_migrated = 0
    total_migrated += migrate_users(sl_conn, pg_conn)
    total_migrated += migrate_lessons(sl_conn, pg_conn)
    total_migrated += migrate_progress(sl_conn, pg_conn)
    total_migrated += migrate_dyslexia_tests(sl_conn, pg_conn)
    
    # Reset sequences
    reset_sequences(pg_conn)
    
    # Close connections
    sl_conn.close()
    pg_conn.close()
    
    print(f"\n🎉 Migration completed! Total records migrated: {total_migrated}")
    print("\nNext steps:")
    print("1. Update .env file: DATABASE_TYPE=postgresql")
    print("2. Update .env file: DATABASE_URL=postgresql://user:password@localhost:5432/lexilearn")
    print("3. Restart the application")


if __name__ == "__main__":
    main()


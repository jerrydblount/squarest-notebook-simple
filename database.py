"""
Simple SQLite database for Squarest Notebook
Replaces SurrealDB with a reliable, zero-config database
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from loguru import logger

# Database path - persists to disk
DB_PATH = Path("data/notebook.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_database():
    """Initialize database with required tables"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Sources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                url TEXT,
                file_type TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Notes table  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                source_id TEXT,
                title TEXT,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES sources(id)
            )
        """)
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                messages TEXT NOT NULL,
                model TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Podcasts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS podcasts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                transcript TEXT,
                audio_url TEXT,
                sources TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        logger.info("Database initialized successfully")


@contextmanager
def get_connection():
    """Get database connection context manager"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()


def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())


# Source operations
def create_source(title: str, content: str = None, url: str = None, 
                  file_type: str = None, metadata: Dict = None) -> str:
    """Create a new source"""
    source_id = generate_id()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sources (id, title, content, url, file_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (source_id, title, content, url, file_type, 
              json.dumps(metadata) if metadata else None))
        conn.commit()
    
    logger.info(f"Created source: {source_id}")
    return source_id


def get_sources() -> List[Dict[str, Any]]:
    """Get all sources"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sources ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
    sources = []
    for row in rows:
        source = dict(row)
        if source.get('metadata'):
            source['metadata'] = json.loads(source['metadata'])
        sources.append(source)
    
    return sources


def get_source(source_id: str) -> Optional[Dict[str, Any]]:
    """Get a single source by ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        
    if row:
        source = dict(row)
        if source.get('metadata'):
            source['metadata'] = json.loads(source['metadata'])
        return source
    return None


def delete_source(source_id: str) -> bool:
    """Delete a source and its notes"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE source_id = ?", (source_id,))
        cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
        conn.commit()
        
    logger.info(f"Deleted source: {source_id}")
    return True


# Note operations
def create_note(content: str, title: str = None, source_id: str = None,
                metadata: Dict = None) -> str:
    """Create a new note"""
    note_id = generate_id()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notes (id, source_id, title, content, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (note_id, source_id, title, content,
              json.dumps(metadata) if metadata else None))
        conn.commit()
    
    logger.info(f"Created note: {note_id}")
    return note_id


def get_notes(source_id: str = None) -> List[Dict[str, Any]]:
    """Get notes, optionally filtered by source"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        if source_id:
            cursor.execute("""
                SELECT * FROM notes 
                WHERE source_id = ? 
                ORDER BY created_at DESC
            """, (source_id,))
        else:
            cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
    
    notes = []
    for row in rows:
        note = dict(row)
        if note.get('metadata'):
            note['metadata'] = json.loads(note['metadata'])
        notes.append(note)
    
    return notes


# Conversation operations
def create_conversation(messages: List[Dict], title: str = None, 
                       model: str = None, metadata: Dict = None) -> str:
    """Create a new conversation"""
    conv_id = generate_id()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (id, title, messages, model, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (conv_id, title, json.dumps(messages), model,
              json.dumps(metadata) if metadata else None))
        conn.commit()
    
    logger.info(f"Created conversation: {conv_id}")
    return conv_id


def get_conversations() -> List[Dict[str, Any]]:
    """Get all conversations"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations ORDER BY created_at DESC")
        rows = cursor.fetchall()
    
    conversations = []
    for row in rows:
        conv = dict(row)
        conv['messages'] = json.loads(conv['messages'])
        if conv.get('metadata'):
            conv['metadata'] = json.loads(conv['metadata'])
        conversations.append(conv)
    
    return conversations


def update_conversation(conv_id: str, messages: List[Dict]) -> bool:
    """Update conversation messages"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE conversations 
            SET messages = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(messages), conv_id))
        conn.commit()
    
    return True


# Podcast operations
def create_podcast(title: str, transcript: str = None, audio_url: str = None,
                  sources: List[str] = None, metadata: Dict = None) -> str:
    """Create a new podcast"""
    podcast_id = generate_id()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO podcasts (id, title, transcript, audio_url, sources, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (podcast_id, title, transcript, audio_url,
              json.dumps(sources) if sources else None,
              json.dumps(metadata) if metadata else None))
        conn.commit()
    
    logger.info(f"Created podcast: {podcast_id}")
    return podcast_id


def get_podcasts() -> List[Dict[str, Any]]:
    """Get all podcasts"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM podcasts ORDER BY created_at DESC")
        rows = cursor.fetchall()
    
    podcasts = []
    for row in rows:
        podcast = dict(row)
        if podcast.get('sources'):
            podcast['sources'] = json.loads(podcast['sources'])
        if podcast.get('metadata'):
            podcast['metadata'] = json.loads(podcast['metadata'])
        podcasts.append(podcast)
    
    return podcasts


# Initialize database on import
init_database()

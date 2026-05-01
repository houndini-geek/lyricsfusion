"""
Database module for Genius lyrics scraper.
Handles SQLite3 operations for storing and retrieving lyrics.
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from utils import SettingsManager

class LyricsDatabase:
    def __init__(self, db_name: str = SettingsManager.load_settings()['db_path']):
        """Initialize database connection and create tables if needed."""
        self.db_path = Path(db_name)
        self.connection = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection."""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def _create_tables(self):
        """Create lyrics table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lyrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist TEXT NOT NULL,
                song_title TEXT NOT NULL,
                lyrics TEXT NOT NULL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                genius_url TEXT,
                UNIQUE(artist, song_title)
            )
        """)
        self.connection.commit()

    def save_lyrics(self, artist: str, song_title: str, lyrics: str, url: str = None) -> bool:
        """
        Save lyrics to database.
        Returns True if successful, False if song already exists.
        """
        try:
            self.cursor.execute("""
                INSERT INTO lyrics (artist, song_title, lyrics, genius_url)
                VALUES (?, ?, ?, ?)
            """, (artist.strip(), song_title.strip(), lyrics, url))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            # Song already exists
            return False
        except Exception as e:
            print(f"Error saving lyrics: {e}")
            return False

    def get_lyrics(self, artist: str, song_title: str) -> dict | None:
        """Retrieve lyrics from database."""
        self.cursor.execute("""
            SELECT * FROM lyrics WHERE artist = ? AND song_title = ?
        """, (artist.strip(), song_title.strip()))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all_lyrics(self) -> list[dict]:
        """Retrieve all stored lyrics."""
        self.cursor.execute("SELECT * FROM lyrics ORDER BY scraped_at DESC")
        return [dict(row) for row in self.cursor.fetchall()]

    def search_lyrics(self, query: str) -> list[dict]:
        """Search lyrics by artist or song title."""
        search_term = f"%{query.lower()}%"
        self.cursor.execute("""
            SELECT * FROM lyrics 
            WHERE LOWER(artist) LIKE ? OR LOWER(song_title) LIKE ?
            ORDER BY scraped_at DESC
        """, (search_term, search_term))
        return [dict(row) for row in self.cursor.fetchall()]

    def delete_lyrics(self, artist: str, song_title: str) -> bool:
        """Delete lyrics from database."""
        try:
            self.cursor.execute("""
                DELETE FROM lyrics WHERE artist = ? AND song_title = ?
            """, (artist.strip(), song_title.strip()))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting lyrics: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

    def __del__(self):
        """Ensure connection closes on object destruction."""
        self.close()

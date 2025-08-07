"""Database connection and schema management."""

import os
import sqlite3
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

import aiosqlite
from loguru import logger


def get_database_path() -> str:
    """Get the database file path from environment or default."""
    db_path = os.getenv("PISTE_MIND_DB_PATH", "~/.piste-mind/sessions.db")
    db_path = Path(db_path).expanduser()

    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return str(db_path)


def create_schema(conn: sqlite3.Connection) -> None:
    """Create database schema if it doesn't exist."""
    conn.execute("PRAGMA foreign_keys = ON")

    # Sessions table - main session tracking
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            state TEXT NOT NULL DEFAULT 'created',
            interface TEXT NOT NULL,
            model_used TEXT NOT NULL DEFAULT 'haiku',
            user_id TEXT,
            
            -- Serialized JSON fields for complex data
            scenario TEXT,          -- JSON
            choices TEXT,           -- JSON
            user_answer TEXT,       -- JSON
            feedback TEXT,          -- JSON
            
            -- Analytics
            time_to_choice REAL,
            time_to_explanation REAL,
            total_session_time REAL,
            
            -- Error tracking
            error_message TEXT,
            error_count INTEGER DEFAULT 0
        )
    """)

    # Session events table - detailed event tracking
    conn.execute("""
        CREATE TABLE IF NOT EXISTS session_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,  -- 'state_change', 'error', 'user_action'
            event_data TEXT,           -- JSON with event details
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)

    # Indexes for performance
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at)"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_state ON sessions(state)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_session_events_session_id ON session_events(session_id)"
    )

    conn.commit()
    logger.info("Database schema created/verified")


@contextmanager
def get_connection() -> Generator[sqlite3.Connection]:
    """Get a database connection (sync)."""
    db_path = get_database_path()
    logger.debug(f"Opening database connection to {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
    finally:
        conn.close()


@asynccontextmanager
async def get_async_connection() -> AsyncGenerator[aiosqlite.Connection]:
    """Get an async database connection."""
    db_path = get_database_path()
    logger.debug(f"Opening async database connection to {db_path}")

    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON")
        yield conn


def initialize_database() -> None:
    """Initialize the database with schema."""
    db_path = get_database_path()
    logger.info(f"Initializing database at {db_path}")

    with get_connection() as conn:
        create_schema(conn)


# Initialize database on module import
initialize_database()

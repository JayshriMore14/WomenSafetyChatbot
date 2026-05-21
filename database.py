"""SQLite database functions for emergency contacts."""

from __future__ import annotations

import sqlite3
import os
from pathlib import Path


def get_database_path() -> Path:
    """Return a reliable local SQLite path.

    OneDrive-synced folders can sometimes cause SQLite disk I/O errors on
    Windows. The default local app-data location avoids that issue. Set
    WOMEN_SAFETY_DB_PATH to override this path.
    """
    configured_path = os.getenv("WOMEN_SAFETY_DB_PATH")
    if configured_path:
        return Path(configured_path)

    base_dir = Path(os.getenv("LOCALAPPDATA", Path.home())) / "WomenSafetyChatbot"
    return base_dir / "safety_contacts.db"


DB_PATH = get_database_path()


def get_connection() -> sqlite3.Connection:
    """Create a database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Create the contacts table if it does not exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                relation TEXT NOT NULL,
                priority INTEGER DEFAULT 1
            )
            """
        )


def add_contact(name: str, phone: str, relation: str, priority: int) -> None:
    """Add a new emergency contact."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO contacts (name, phone, relation, priority) VALUES (?, ?, ?, ?)",
            (name.strip(), phone.strip(), relation.strip(), int(priority)),
        )


def update_contact(contact_id: int, name: str, phone: str, relation: str, priority: int) -> None:
    """Update an existing emergency contact."""
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE contacts
            SET name = ?, phone = ?, relation = ?, priority = ?
            WHERE id = ?
            """,
            (name.strip(), phone.strip(), relation.strip(), int(priority), int(contact_id)),
        )


def delete_contact(contact_id: int) -> None:
    """Delete an emergency contact."""
    with get_connection() as conn:
        conn.execute("DELETE FROM contacts WHERE id = ?", (int(contact_id),))


def get_contacts() -> list[dict]:
    """Fetch contacts ordered by priority."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, name, phone, relation, priority FROM contacts ORDER BY priority, name"
        ).fetchall()
    return [dict(row) for row in rows]

"""
Database module for Mergington High School API.

Provides SQLite-backed persistence for activities and participant signups.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "school.db"

SEED_ACTIVITIES = [
    ("Chess Club", "Learn strategies and compete in chess tournaments", "Fridays, 3:30 PM - 5:00 PM", 12),
    ("Programming Class", "Learn programming fundamentals and build software projects", "Tuesdays and Thursdays, 3:30 PM - 4:30 PM", 20),
    ("Gym Class", "Physical education and sports activities", "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", 30),
    ("Soccer Team", "Join the school soccer team and compete in matches", "Tuesdays and Thursdays, 4:00 PM - 5:30 PM", 22),
    ("Basketball Team", "Practice and play basketball with the school team", "Wednesdays and Fridays, 3:30 PM - 5:00 PM", 15),
    ("Art Club", "Explore your creativity through painting and drawing", "Thursdays, 3:30 PM - 5:00 PM", 15),
    ("Drama Club", "Act, direct, and produce plays and performances", "Mondays and Wednesdays, 4:00 PM - 5:30 PM", 20),
    ("Math Club", "Solve challenging problems and participate in math competitions", "Tuesdays, 3:30 PM - 4:30 PM", 10),
    ("Debate Team", "Develop public speaking and argumentation skills", "Fridays, 4:00 PM - 5:30 PM", 12),
]

SEED_PARTICIPANTS = [
    ("Chess Club", "michael@mergington.edu"),
    ("Chess Club", "daniel@mergington.edu"),
    ("Programming Class", "emma@mergington.edu"),
    ("Programming Class", "sophia@mergington.edu"),
    ("Gym Class", "john@mergington.edu"),
    ("Gym Class", "olivia@mergington.edu"),
    ("Soccer Team", "liam@mergington.edu"),
    ("Soccer Team", "noah@mergington.edu"),
    ("Basketball Team", "ava@mergington.edu"),
    ("Basketball Team", "mia@mergington.edu"),
    ("Art Club", "amelia@mergington.edu"),
    ("Art Club", "harper@mergington.edu"),
    ("Drama Club", "ella@mergington.edu"),
    ("Drama Club", "scarlett@mergington.edu"),
    ("Math Club", "james@mergington.edu"),
    ("Math Club", "benjamin@mergington.edu"),
    ("Debate Team", "charlotte@mergington.edu"),
    ("Debate Team", "henry@mergington.edu"),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables if they do not already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                name             TEXT PRIMARY KEY,
                description      TEXT NOT NULL,
                schedule         TEXT NOT NULL,
                max_participants INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                activity_name TEXT NOT NULL REFERENCES activities(name),
                email         TEXT NOT NULL,
                PRIMARY KEY (activity_name, email)
            )
        """)


def seed_data() -> None:
    """Insert default activities and participants; safe to call on every startup."""
    with get_connection() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO activities (name, description, schedule, max_participants) VALUES (?, ?, ?, ?)",
            SEED_ACTIVITIES,
        )
        conn.executemany(
            "INSERT OR IGNORE INTO participants (activity_name, email) VALUES (?, ?)",
            SEED_PARTICIPANTS,
        )


def get_activities() -> dict:
    """Return all activities with their participant lists as a dict."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM activities").fetchall()
        result = {}
        for row in rows:
            participants = conn.execute(
                "SELECT email FROM participants WHERE activity_name = ?", (row["name"],)
            ).fetchall()
            result[row["name"]] = {
                "description": row["description"],
                "schedule": row["schedule"],
                "max_participants": row["max_participants"],
                "participants": [p["email"] for p in participants],
            }
        return result


def get_activity(name: str) -> dict | None:
    """Return a single activity dict, or None if not found."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM activities WHERE name = ?", (name,)).fetchone()
        if row is None:
            return None
        participants = conn.execute(
            "SELECT email FROM participants WHERE activity_name = ?", (name,)
        ).fetchall()
        return {
            "description": row["description"],
            "schedule": row["schedule"],
            "max_participants": row["max_participants"],
            "participants": [p["email"] for p in participants],
        }


def add_participant(activity_name: str, email: str) -> None:
    """Add a participant to an activity. Raises ValueError on duplicate."""
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO participants (activity_name, email) VALUES (?, ?)",
                (activity_name, email),
            )
        except sqlite3.IntegrityError:
            raise ValueError("Student is already signed up")


def remove_participant(activity_name: str, email: str) -> bool:
    """Remove a participant from an activity. Returns True if removed, False if not found."""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM participants WHERE activity_name = ? AND email = ?",
            (activity_name, email),
        )
        return cursor.rowcount > 0

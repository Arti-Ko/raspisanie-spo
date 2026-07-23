import os
import sqlite3
import sys
from pathlib import Path

APP_DIR_NAME = "RaspisanieSPO"


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def _user_data_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", str(Path.home()))
        return Path(base) / APP_DIR_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DIR_NAME
    return Path.home() / ".local" / "share" / APP_DIR_NAME


def _bundled_schema_dir() -> Path:
    if _is_frozen():
        return Path(sys._MEIPASS) / "app" / "db"
    return Path(__file__).resolve().parent


DB_PATH = (
    _user_data_dir() / "raspisanie.db"
    if _is_frozen()
    else Path(__file__).resolve().parent.parent.parent / "data" / "raspisanie.db"
)
SCHEMA_PATH = _bundled_schema_dir() / "schema.sql"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        _apply_migrations(conn)
        conn.commit()
    finally:
        conn.close()


def _apply_migrations(conn: sqlite3.Connection) -> None:
    _add_column_if_missing(
        conn, "curriculum_items", "lesson_type", "TEXT NOT NULL DEFAULT 'theory'"
    )
    _add_column_if_missing(
        conn, "curriculum_items", "is_double_pair", "INTEGER NOT NULL DEFAULT 0"
    )
    _add_column_if_missing(conn, "teachers", "color", "TEXT")
    _add_column_if_missing(
        conn,
        "calendar_weeks",
        "includes_saturday",
        "INTEGER NOT NULL DEFAULT 1",
    )
    _add_column_if_missing(conn, "calendar_weeks", "start_date", "TEXT")

    _migrate_schedule_entries_pair_range(conn)
    _migrate_bell_schedule_lessons_pair_range(conn)


def _add_column_if_missing(
    conn: sqlite3.Connection, table: str, column: str, ddl: str
) -> None:
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def _migrate_schedule_entries_pair_range(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'schedule_entries'"
    ).fetchone()
    if row is None or "BETWEEN 0 AND 4" in row["sql"]:
        return

    conn.execute("DELETE FROM schedule_entries WHERE pair_number = 5")
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("""
        CREATE TABLE schedule_entries_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calendar_week_id INTEGER NOT NULL REFERENCES calendar_weeks(id) ON DELETE CASCADE,
            group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
            assignment_id INTEGER NOT NULL REFERENCES teacher_assignments(id) ON DELETE CASCADE,
            day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 6),
            pair_number INTEGER NOT NULL CHECK (pair_number BETWEEN 0 AND 4),
            room TEXT,
            substitute_teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
            UNIQUE (group_id, calendar_week_id, day_of_week, pair_number)
        )
        """)
    conn.execute("INSERT INTO schedule_entries_new SELECT * FROM schedule_entries")
    conn.execute("DROP TABLE schedule_entries")
    conn.execute("ALTER TABLE schedule_entries_new RENAME TO schedule_entries")
    conn.execute("PRAGMA foreign_keys = ON")


def _migrate_bell_schedule_lessons_pair_range(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'bell_schedule_lessons'"
    ).fetchone()
    if row is None or "BETWEEN 1 AND 4" in row["sql"]:
        return

    conn.execute("DELETE FROM bell_schedule_lessons WHERE pair_number = 5")
    conn.execute("""
        CREATE TABLE bell_schedule_lessons_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 6),
            pair_number INTEGER NOT NULL CHECK (pair_number BETWEEN 1 AND 4),
            lesson_number INTEGER NOT NULL CHECK (lesson_number IN (1, 2)),
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            UNIQUE (day_of_week, pair_number, lesson_number)
        )
        """)
    conn.execute(
        "INSERT INTO bell_schedule_lessons_new SELECT * FROM bell_schedule_lessons"
    )
    conn.execute("DROP TABLE bell_schedule_lessons")
    conn.execute(
        "ALTER TABLE bell_schedule_lessons_new RENAME TO bell_schedule_lessons"
    )

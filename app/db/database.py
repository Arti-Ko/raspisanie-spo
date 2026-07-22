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
    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(curriculum_items)")
    }
    if "lesson_type" not in columns:
        conn.execute(
            "ALTER TABLE curriculum_items ADD COLUMN lesson_type TEXT NOT NULL DEFAULT 'theory'"
        )

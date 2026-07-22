from dataclasses import dataclass

from app.db.database import get_connection


@dataclass(frozen=True)
class BellTime:
    pair_number: int
    start_time: str
    end_time: str

    @property
    def label(self) -> str:
        return f"{self.start_time}–{self.end_time}"


def list_bell_times() -> list[BellTime]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT pair_number, start_time, end_time FROM bell_times ORDER BY pair_number"
        ).fetchall()
        return [
            BellTime(row["pair_number"], row["start_time"], row["end_time"])
            for row in rows
        ]
    finally:
        conn.close()


def update_bell_time(pair_number: int, start_time: str, end_time: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE bell_times SET start_time = ?, end_time = ? WHERE pair_number = ?",
            (start_time, end_time, pair_number),
        )
        conn.commit()
    finally:
        conn.close()

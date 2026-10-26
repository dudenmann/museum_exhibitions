import argparse
from dataclasses import asdict
from pathlib import Path

from db.database import ROOT, connection, database_path
from storage import DEFAULT_PATH, load_museum


def import_data(source=DEFAULT_PATH, target=None):
    museum = load_museum(source)
    target = Path(target or database_path())
    target.parent.mkdir(parents=True, exist_ok=True)
    with connection(target) as conn:
        conn.executescript((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            if any(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                   for table in ("halls", "curators", "exhibitions")):
                raise ValueError("База уже содержит данные. Импорт не изменил их.")
            conn.executemany(
                "INSERT INTO halls VALUES (?, ?, ?, ?, ?)",
                [(h.id, h.name, h.capacity, h.hall_type, h.description)
                 for h in museum.halls],
            )
            conn.executemany(
                "INSERT INTO curators VALUES (?, ?, ?)",
                [(c.id, c.name, c.email) for c in museum.curators],
            )
            conn.executemany(
                "INSERT INTO exhibitions VALUES "
                "(:id, :title, :hall_id, :curator_id, :start_date, :end_date, "
                ":description, :is_cancelled)",
                [{**asdict(e), "start_date": e.start_date.isoformat(),
                  "end_date": e.end_date.isoformat()} for e in museum.exhibitions],
            )
            conn.commit()
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Импорт JSON в пустую SQLite-базу")
    parser.add_argument("--source", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--target", type=Path)
    args = parser.parse_args()
    try:
        print(f"Данные импортированы: {import_data(args.source, args.target)}")
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")

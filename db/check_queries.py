"""Воспроизводимая проверка каждого SQL-запроса через консоль."""

from db.database import connection
from db.repository import queries

PARAMETERS = {
    "halls_capacity": (30,),
    "available_halls": ("2026-11-10", "2026-11-05"),
    "exhibition_catalog": (12, 0),
    "exhibition_detail": (1,),
    "exhibitions_by_curator": (0,),
    "exhibition_search": ("%город%", 12, 0),
    "hall_detail": (1,),
}


if __name__ == "__main__":
    with connection() as conn:
        for name, sql in queries().items():
            rows = conn.execute(sql, PARAMETERS.get(name, ())).fetchall()
            print(f"{name}: {len(rows)} строк")
            for row in rows:
                print(dict(row))

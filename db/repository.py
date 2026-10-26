from datetime import date
from functools import lru_cache

from db.database import ROOT, connection


@lru_cache(maxsize=1)
def queries():
    text = (ROOT / "sql" / "queries.sql").read_text(encoding="utf-8")
    result = {}
    for part in text.split("-- name: ")[1:]:
        name, sql = part.split("\n", 1)
        result[name.strip()] = sql.strip()
    return result


def select(name, parameters=()):
    with connection() as conn:
        rows = conn.execute(queries()[name], parameters).fetchall()
    # sqlite3.Row предоставляет поля по именам; даты готовим для фильтра date.
    result = []
    for row in rows:
        item = dict(row)
        for key in ("start_date", "end_date"):
            if key in item:
                item[key] = date.fromisoformat(item[key])
        result.append(item)
    return result


def one(name, parameters=()):
    rows = select(name, parameters)
    return rows[0] if rows else None


def exhibitions(query="", limit=12, offset=0):
    if not query:
        return select("exhibition_catalog", (limit, offset))
    escaped = query.casefold().replace("!", "!!")
    escaped = escaped.replace("%", "!%").replace("_", "!_")
    return select("exhibition_search", (f"%{escaped}%", limit, offset))


def available(start, end):
    if start > end:
        raise ValueError("Начало периода должно быть не позже окончания.")
    return select("available_halls", (end.isoformat(), start.isoformat()))

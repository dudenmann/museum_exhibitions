from datetime import date

from django.core.cache import cache

from db.database import connection
from models import Exhibition, Hall, Curator


def text(data, key, maximum=500):
    value = data.get(key, "")
    if not isinstance(value, str) or len(value) > maximum:
        raise ValueError(f"Поле {key}: требуется строка до {maximum} символов.")
    return value.strip()


def integer(data, key):
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError(f"Поле {key}: требуется целое число.")
    try:
        return int(value)
    except (ValueError, OverflowError) as error:
        raise ValueError(f"Поле {key}: требуется целое число.") from error


def invalidate_statistics():
    cache.delete("museum:statistics")


def create_exhibition(data):
    item = Exhibition(
        1, text(data, "title", 200), integer(data, "hall_id"),
        integer(data, "curator_id"), date.fromisoformat(text(data, "start_date")),
        date.fromisoformat(text(data, "end_date")), text(data, "description", 5000),
    )
    with connection() as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.execute(
            "INSERT INTO exhibitions "
            "(title, hall_id, curator_id, start_date, end_date, description) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (item.title, item.hall_id, item.curator_id, item.start_date.isoformat(),
             item.end_date.isoformat(), item.description),
        )
        item_id = cursor.lastrowid
    invalidate_statistics()
    return item_id


def cancel_exhibition(item_id):
    with connection() as conn, conn:
        result = conn.execute(
            "UPDATE exhibitions SET is_cancelled=1 WHERE id=?", (item_id,),
        )
        if result.rowcount == 0:
            raise LookupError("Выставка не найдена.")
    invalidate_statistics()


def create_hall(data):
    item = Hall(1, text(data, "name", 200), integer(data, "capacity"),
                text(data, "hall_type", 100) or "Универсальный",
                text(data, "description", 5000))
    with connection() as conn, conn:
        result = conn.execute(
            "INSERT INTO halls (name, capacity, hall_type, description) "
            "VALUES (?, ?, ?, ?)",
            (item.name, item.capacity, item.hall_type, item.description),
        )
        item_id = result.lastrowid
    invalidate_statistics()
    return item_id


def create_curator(data):
    item = Curator(1, text(data, "name", 200), text(data, "email", 254))
    with connection() as conn, conn:
        result = conn.execute("INSERT INTO curators (name, email) VALUES (?, ?)",
                              (item.name, item.email))
        item_id = result.lastrowid
    invalidate_statistics()
    return item_id

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def database_path():
    return Path(os.environ.get("MUSEUM_DB", ROOT / "data" / "museum.sqlite3"))


def get_connection(path=None):
    connection = sqlite3.connect(path or database_path(), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.create_function("CASEFOLD", 1, lambda text: (text or "").casefold())
    return connection


@contextmanager
def connection(path=None):
    conn = get_connection(path)
    try:
        yield conn
    finally:
        conn.close()

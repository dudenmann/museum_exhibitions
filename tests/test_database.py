import sqlite3
from datetime import date

import pytest

from db.database import connection
from db.import_json import import_data
from db import repository as repo
from storage import DEMO_PATH

pytestmark = pytest.mark.usefixtures("database")


def test_import_is_non_destructive(database):
    with pytest.raises(ValueError, match="уже содержит"):
        import_data(DEMO_PATH, database)
    assert repo.one("exhibition_totals")["count"] == 4


def test_foreign_keys_and_overlap_are_enforced():
    with connection() as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE exhibitions SET hall_id=999 WHERE id=1")
        conn.rollback()
        with pytest.raises(sqlite3.IntegrityError, match="занят"):
            conn.execute("UPDATE exhibitions SET hall_id=1 WHERE id=2")
        conn.rollback()


def test_available_boundary_and_cancelled():
    rows = repo.available(date(2026, 11, 5), date(2026, 11, 10))
    assert [row["id"] for row in rows] == [3]
    assert 1 not in {r["id"] for r in repo.available(
        date(2026, 11, 15), date(2026, 11, 15))}
    assert 1 in {r["id"] for r in repo.available(
        date(2026, 11, 16), date(2026, 11, 16))}


def test_sql_search_unicode_and_injection():
    assert len(repo.exhibitions("ГОРОД")) == 2
    assert repo.exhibitions("%' OR 1=1 --") == []
    assert repo.exhibitions("%") == []
    assert repo.exhibitions("_") == []


def test_all_named_queries_have_expected_results():
    assert len(repo.select("halls_list")) == 3
    assert len(repo.select("curators_list")) == 2
    assert len(repo.select("halls_capacity", (30,))) == 2
    assert repo.one("hall_totals")["total"] == 145
    assert repo.one("exhibition_totals")["active"] == 3
    assert repo.one("exhibition_detail", (1,))["curator_name"] == "Анна Соколова"
    assert repo.one("hall_detail", (1,))["capacity"] == 80
    assert repo.one("missing_descriptions")["count"] == 0
    assert [r["count"] for r in repo.select("exhibitions_by_hall")] == [2, 1, 0]
    assert repo.select("exhibitions_by_curator", (2,))[0]["name"] == "Иван Петров"
    assert len(repo.exhibitions(limit=2, offset=2)) == 2
    assert len(repo.queries()) == 13

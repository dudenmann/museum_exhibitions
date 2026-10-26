import os

import django
import pytest

from db.import_json import import_data
from db.database import ROOT, connection
from storage import DEMO_PATH

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum_site.settings")
django.setup()


@pytest.fixture
def database(tmp_path, monkeypatch):
    target = tmp_path / "test.sqlite3"
    monkeypatch.setenv("MUSEUM_DB", str(target))
    import_data(DEMO_PATH, target)
    with connection(target) as conn:
        conn.executescript((ROOT / "sql" / "accounts.sql").read_text(encoding="utf-8"))
    from django.core.cache import cache
    cache.clear()
    return target

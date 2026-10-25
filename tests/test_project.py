import json
from datetime import date

import pytest

from models import Curator, Hall
from services import Museum
from storage import DEMO_PATH, load_museum, save_museum


def day(value):
    return date.fromisoformat(value)


@pytest.fixture
def museum():
    return Museum([Hall(1, "Зал", 20)], [Curator(1, "Анна", "a@example.com")])


def create(museum, start="2026-11-05", end="2026-11-10", **kwargs):
    return museum.create_exhibition(
        kwargs.get("title", "Живопись"), kwargs.get("hall_id", 1),
        kwargs.get("curator_id", 1), day(start), day(end),
    )


@pytest.mark.parametrize("start,end", [
    ("2026-11-01", "2026-11-05"),
    ("2026-11-10", "2026-11-15"),
    ("2026-11-06", "2026-11-07"),
    ("2026-11-01", "2026-11-20"),
])
def test_overlap_including_boundaries_is_rejected(museum, start, end):
    create(museum)
    with pytest.raises(ValueError, match="занят"):
        create(museum, start, end)
    assert len(museum.exhibitions) == 1


def test_next_day_is_available_and_cancellation_releases_hall(museum):
    item = create(museum)
    create(museum, "2026-11-11", "2026-11-11")
    assert museum.available_halls(day("2026-11-05"), day("2026-11-05")) == []
    museum.cancel_exhibition(item.id)
    assert len(museum.available_halls(day("2026-11-05"), day("2026-11-05"))) == 1
    assert museum.get_exhibition(item.id).is_cancelled


@pytest.mark.parametrize("kwargs", [{"hall_id": 99}, {"curator_id": 99}])
def test_missing_reference_is_rejected(museum, kwargs):
    with pytest.raises(ValueError, match="не найден"):
        create(museum, **kwargs)
    assert not museum.exhibitions


def test_invalid_period_and_blank_title_are_rejected(museum):
    with pytest.raises(ValueError):
        create(museum, "2026-11-10", "2026-11-01")
    with pytest.raises(ValueError):
        create(museum, title=" ")


def test_search_is_case_insensitive_and_excludes_cancelled(museum):
    item = create(museum)
    assert museum.search_exhibitions("ЖИВО") == [item]
    museum.cancel_exhibition(item.id)
    assert museum.search_exhibitions("живо") == []
    assert len(museum.search_exhibitions("живо", include_cancelled=True)) == 1


def test_round_trip_preserves_dates_unicode_and_cancellation(museum, tmp_path):
    item = create(museum)
    museum.cancel_exhibition(item.id)
    path = tmp_path / "museum.json"
    save_museum(museum, path)
    restored = load_museum(path)
    assert restored.halls == museum.halls
    assert restored.curators == museum.curators
    assert restored.exhibitions == museum.exhibitions


def test_broken_file_is_not_replaced_with_demo(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="Некорректные данные"):
        load_museum(path)
    assert path.read_text(encoding="utf-8") == "{"


def test_import_rejects_duplicate_ids(tmp_path):
    data = json.loads(DEMO_PATH.read_text(encoding="utf-8"))
    data["halls"].append(data["halls"][0])
    path = tmp_path / "duplicate.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="повторяющиеся"):
        load_museum(path)


def test_demo_data_is_consistent():
    museum = load_museum(DEMO_PATH)
    assert len(museum.halls) == 3
    assert len(museum.exhibitions) == 4

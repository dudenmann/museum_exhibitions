import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from django.contrib.auth.hashers import make_password
from django.test import Client, override_settings

from db.database import connection
from db import mutations, repository as repo
from db.statistics import summary

pytestmark = pytest.mark.usefixtures("database")


@pytest.fixture
def accounts():
    with override_settings(PASSWORD_HASHERS=[
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]):
        with connection() as conn, conn:
            conn.executemany(
                "INSERT INTO accounts(username,password_hash,role) VALUES (?,?,?)",
                [(role, make_password("test-password-123"), role)
                 for role in ("viewer", "editor")],
            )
        yield


def login(role="editor", strict=False):
    client = Client(enforce_csrf_checks=strict)
    client.get("/accounts/login/")
    response = client.post("/accounts/login/", {
        "username": role, "password": "test-password-123",
        "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
    })
    assert response.status_code == 302
    return client


def payload():
    return {"title": "Новая выставка", "hall_id": 1, "curator_id": 1,
            "start_date": "2027-01-01", "end_date": "2027-01-10"}


def post(client, data=None, csrf=True):
    extra = {}
    if csrf and "csrftoken" in client.cookies:
        extra["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
    return client.post("/api/exhibitions/", json.dumps(data or payload()),
                       content_type="application/json", **extra)


def test_authentication_and_authorization(accounts):
    assert post(Client()).status_code == 401
    assert post(login("viewer")).status_code == 403
    assert post(login()).status_code == 201


def test_csrf_required_even_for_editor(accounts):
    client = login(strict=True)
    assert post(client, csrf=False).status_code == 403
    assert post(client).status_code == 201


def test_create_conflict_cancel_and_rebook(accounts):
    client = login()
    first = post(client)
    item_id = first.json()["id"]
    assert post(client).status_code == 409
    response = client.patch(f"/api/exhibitions/{item_id}/",
                            '{"is_cancelled": true}', content_type="application/json")
    assert response.status_code == 200
    assert post(client).status_code == 201


@pytest.mark.parametrize("data", [
    {"title": ""}, {"hall_id": 999}, {"curator_id": 999},
    {"start_date": "bad"}, {"end_date": "2026-01-01"},
    {"hall_id": True}, {"title": ["wrong"]},
])
def test_invalid_input_does_not_create_records(accounts, data):
    client = login()
    response = post(client, {**payload(), **data})
    assert response.status_code in (400, 409)
    assert repo.one("exhibition_totals")["count"] == 4


def test_method_and_json_validation(accounts):
    client = login()
    assert client.delete("/api/exhibitions/1/").status_code == 405
    assert client.post("/api/exhibitions/", "{",
                       content_type="application/json").status_code == 400
    assert client.get("/api/exhibitions/?limit=9999").status_code == 400
    assert client.get("/api/exhibitions/99999/").status_code == 404


def test_template_escapes_user_text(accounts):
    client = login()
    response = post(client, {**payload(), "title": "<script>alert(1)</script>"})
    page = client.get(f'/exhibitions/{response.json()["id"]}/').content.decode()
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_statistics_cache_is_invalidated(accounts):
    assert summary()["exhibitions"]["count"] == 4
    assert post(login()).status_code == 201
    assert summary()["exhibitions"]["count"] == 5


def test_logout_and_rate_limit(accounts):
    client = login()
    assert client.get("/accounts/logout/").status_code == 405
    assert client.post("/accounts/logout/").status_code == 302
    assert post(client).status_code == 401
    for _ in range(8):
        assert client.post("/accounts/login/", {
            "username": "editor", "password": "wrong",
        }).status_code == 400
    assert client.post("/accounts/login/", {}).status_code == 429


def test_concurrent_booking_keeps_single_exhibition():
    def attempt(_):
        try:
            mutations.create_exhibition(payload())
            return True
        except Exception as error:
            import sqlite3
            assert isinstance(error, sqlite3.IntegrityError)
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert sum(results) == 1
    assert repo.one("exhibition_totals")["count"] == 5


def test_create_hall_and_curator(accounts):
    client = login()
    response = client.post("/api/halls/", json.dumps({
        "name": "Новый зал", "capacity": 10,
    }), content_type="application/json")
    assert response.status_code == 201
    response = client.post("/api/curators/", json.dumps({
        "name": "Тестовый куратор", "email": "test@example.com",
    }), content_type="application/json")
    assert response.status_code == 201

import os

import django
import pytest
from django.test import Client, override_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum_site.settings")
django.setup()
pytestmark = pytest.mark.usefixtures("database")


@pytest.mark.parametrize("url", [
    "/", "/halls/", "/halls/1/", "/exhibitions/", "/exhibitions/1/",
    "/halls/available/", "/statistics/", "/curators/",
    "/halls/?capacity=30", "/exhibitions/?q=город",
])
def test_pages_open(url):
    assert Client().get(url).status_code == 200


@pytest.mark.parametrize("url", ["/missing/", "/halls/99999/", "/exhibitions/99999/"])
def test_missing_pages(url):
    with override_settings(DEBUG=False):
        response = Client().get(url)
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()


def test_invalid_dates():
    response = Client().get("/halls/available/?start=bad&end=2026-11-10")
    assert response.status_code == 400

from django.core.cache import cache

from db import repository as repo


def summary():
    result = cache.get("museum:statistics")
    if result is None:
        result = {
            "halls": repo.one("hall_totals"),
            "exhibitions": repo.one("exhibition_totals"),
            "by_hall": repo.select("exhibitions_by_hall"),
            "missing": repo.one("missing_descriptions")["count"],
        }
        cache.set("museum:statistics", result, timeout=30)
    return result

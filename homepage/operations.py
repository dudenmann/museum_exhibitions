import logging
import sqlite3
from time import perf_counter

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from accounts.security import editor_required
from db import repository as repo
from db.database import connection

logger = logging.getLogger("museum")


@require_GET
def health(request):
    try:
        with connection() as conn:
            conn.execute("SELECT id FROM exhibitions LIMIT 1").fetchall()
        return JsonResponse({"status": "ok", "database": "ok"})
    except sqlite3.Error:
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)


@editor_required
def workspace(request):
    return render(request, "homepage/workspace.html", {
        "halls": repo.select("halls_list"), "curators": repo.select("curators_list"),
    })


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = perf_counter()
        response = self.get_response(request)
        logger.info("%s %s status=%s duration_ms=%.2f", request.method,
                    request.path, response.status_code, (perf_counter() - start) * 1000)
        return response

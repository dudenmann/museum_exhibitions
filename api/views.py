import json
import logging
import sqlite3
from functools import wraps

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache

from accounts.security import editor_required
from db import repository as repo
from db import mutations

logger = logging.getLogger("museum")


def errors(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except (ValueError, TypeError, UnicodeDecodeError) as error:
            return JsonResponse({"error": str(error)}, status=400)
        except LookupError:
            return JsonResponse({"error": "Запись не найдена."}, status=404)
        except sqlite3.IntegrityError:
            return JsonResponse({"error": "Зал занят или связанные записи неверны."},
                                status=409)
        except sqlite3.OperationalError:
            logger.exception("Database operation failed")
            return JsonResponse({"error": "База временно недоступна."}, status=503)
    return wrapped


def payload(request):
    if request.content_type != "application/json":
        raise ValueError("Требуется Content-Type: application/json.")
    data = json.loads(request.body)
    if not isinstance(data, dict):
        raise ValueError("Ожидается JSON-объект.")
    return data


@editor_required
def create(request, kind):
    handlers = {"exhibitions": mutations.create_exhibition,
                "halls": mutations.create_hall, "curators": mutations.create_curator}
    item_id = handlers[kind](payload(request))
    logger.info("Created %s id=%s", kind, item_id)
    response = JsonResponse({"id": item_id}, status=201)
    if kind == "exhibitions":
        response["Location"] = f"/api/exhibitions/{item_id}/"
    return response


@never_cache
@require_http_methods(["GET", "POST"])
@errors
def exhibitions(request):
    if request.method == "POST":
        return create(request, "exhibitions")
    limit = int(request.GET.get("limit", "12"))
    offset = int(request.GET.get("offset", "0"))
    if not 1 <= limit <= 100 or not 0 <= offset <= 1000000:
        raise ValueError("limit: 1–100; offset: 0–1000000.")
    return JsonResponse({"items": repo.exhibitions(
        request.GET.get("q", ""), limit, offset,
    )})


@editor_required
def cancel(request, item_id):
    data = payload(request)
    if data != {"is_cancelled": True}:
        raise ValueError('Поддерживается только {"is_cancelled": true}.')
    mutations.cancel_exhibition(item_id)
    logger.info("Cancelled exhibition id=%s", item_id)
    return JsonResponse({"id": item_id, "is_cancelled": True})


@never_cache
@require_http_methods(["GET", "PATCH"])
@errors
def exhibition_detail(request, item_id):
    if request.method == "PATCH":
        return cancel(request, item_id)
    item = repo.one("exhibition_detail", (item_id,))
    if item is None:
        raise LookupError
    return JsonResponse(item)


@never_cache
@require_http_methods(["GET", "POST"])
@errors
def halls(request):
    if request.method == "POST":
        return create(request, "halls")
    return JsonResponse({"items": repo.select("halls_list")})


@never_cache
@require_http_methods(["GET", "POST"])
@errors
def curators(request):
    if request.method == "POST":
        return create(request, "curators")
    return JsonResponse({"items": repo.select("curators_list")})

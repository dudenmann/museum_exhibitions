from django.http import Http404
from django.shortcuts import render
from db import repository as repo


def index(request):
    query = request.GET.get("q", "")
    try:
        page = int(request.GET.get("page", "1"))
        if page < 1 or page > 100000:
            raise ValueError
    except ValueError:
        return render(request, "400.html", status=400)
    items = repo.exhibitions(query, limit=13, offset=(page - 1) * 12)
    return render(request, "exhibitions/list.html", {
        "items": items[:12], "q": query, "page": page,
        "previous": page - 1 if page > 1 else None,
        "following": page + 1 if len(items) > 12 else None,
    })


def detail(request, item_id):
    item = repo.one("exhibition_detail", (item_id,))
    if item is None:
        raise Http404
    return render(request, "exhibitions/detail.html", {
        "item": item, "hall": {"id": item["hall_id"], "name": item["hall_name"]},
        "curator": {"name": item["curator_name"]},
    })

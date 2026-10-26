from datetime import date
from django.http import Http404
from django.shortcuts import render
from db import repository as repo


def index(request):
    capacity = request.GET.get("capacity", "")
    try:
        if capacity:
            value = int(capacity)
            if value < 1:
                raise ValueError
            items = repo.select("halls_capacity", (value,))
        else:
            items = repo.select("halls_list")
    except ValueError:
        return render(request, "400.html", status=400)
    return render(request, "halls/list.html", {"items": items, "capacity": capacity})


def detail(request, item_id):
    item = repo.one("hall_detail", (item_id,))
    if item is None:
        raise Http404
    return render(request, "halls/detail.html", {"item": item})


def available(request):
    context = {"searched": bool(request.GET), "items": [],
               "start": request.GET.get("start", ""),
               "end": request.GET.get("end", "")}
    status = 200
    if request.GET:
        try:
            start = date.fromisoformat(context["start"])
            end = date.fromisoformat(context["end"])
            context["items"] = repo.available(start, end)
        except ValueError:
            context["error"] = "Укажите корректные даты: начало не позже окончания."
            status = 400
    return render(request, "halls/available.html", context, status=status)

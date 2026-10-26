from django.shortcuts import render
from db import repository as repo
from db.statistics import summary


def index(request):
    return render(request, "homepage/index.html", {
        "hall_count": repo.one("hall_totals")["count"],
        "exhibition_count": repo.one("exhibition_totals")["count"],
        "curator_count": len(repo.select("curators_list")),
        "items": repo.exhibitions(limit=3),
    })


def curators(request):
    return render(request, "homepage/curators.html", {
        "items": repo.select("curators_list"),
    })


def statistics(request):
    try:
        minimum = int(request.GET.get("minimum", "0"))
        if minimum < 0:
            raise ValueError
    except ValueError:
        return render(request, "400.html", status=400)
    return render(request, "homepage/statistics.html", {
        **summary(),
        "by_curator": repo.select("exhibitions_by_curator", (minimum,)),
        "minimum": minimum,
    })


def not_found(request, exception):
    return render(request, "404.html", status=404)

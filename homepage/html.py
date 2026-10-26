from html import escape

from django.http import HttpResponse


def page(title, body, status=200):
    return HttpResponse(
        '<!doctype html><html lang="ru"><meta charset="utf-8">'
        f'<title>{escape(title)}</title><link rel="stylesheet" '
        'href="/static/style.css"><body><nav><a href="/">Музей</a> '
        '<a href="/halls/">Залы</a> <a href="/exhibitions/">Выставки</a>'
        '<a href="/halls/available/">Свободные залы</a></nav><main>'
        f'<h1>{escape(title)}</h1>{body}</main></body></html>', status=status,
    )

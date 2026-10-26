from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from db.database import connection

# Для неизвестного пользователя тоже проверяем хеш: не раскрываем наличие логина.
DUMMY_HASH = make_password("unused-account-password")


@csrf_protect
def login(request):
    if request.method == "GET":
        return render(request, "accounts/login.html")
    if request.method != "POST":
        return render(request, "400.html", status=405)
    key = "login:" + request.META.get("REMOTE_ADDR", "local")
    if cache.get(key, 0) >= 8:
        return render(request, "accounts/login.html", {
            "error": "Слишком много попыток. Подождите 5 минут.",
        }, status=429)
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM accounts WHERE username = ?", (username,),
        ).fetchone()
    valid = check_password(password, row["password_hash"] if row else DUMMY_HASH)
    if not valid or row is None:
        cache.set(key, cache.get(key, 0) + 1, 300)
        return render(request, "accounts/login.html", {
            "error": "Неверный логин или пароль.",
        }, status=400)
    cache.delete(key)
    request.session.flush()
    request.session["account_id"] = row["id"]
    request.session.set_expiry(3600)
    return redirect("homepage:index")


@require_POST
def logout(request):
    request.session.flush()
    return redirect("homepage:index")

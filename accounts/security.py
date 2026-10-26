from functools import wraps

from django.http import JsonResponse
from django.shortcuts import redirect

from db.database import connection


def current_account(request):
    account_id = request.session.get("account_id")
    if account_id is None:
        return None
    with connection() as conn:
        row = conn.execute(
            "SELECT id, username, role FROM accounts WHERE id = ?", (account_id,),
        ).fetchone()
    return dict(row) if row else None


def account_context(request):
    return {"account": current_account(request)}


def editor_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        account = current_account(request)
        if account is None:
            if request.path.startswith("/api/"):
                return JsonResponse({"error": "Необходимо войти."}, status=401)
            return redirect("accounts:login")
        if account["role"] != "editor":
            return JsonResponse({"error": "Нужна роль редактора."}, status=403)
        return view(request, *args, **kwargs)
    return wrapped

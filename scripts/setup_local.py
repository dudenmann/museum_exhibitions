"""Подготовка локальной установки. Не перезаписывает существующие данные."""
import os
import secrets
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum_site.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth.hashers import make_password  # noqa: E402
from db.database import ROOT, connection, database_path  # noqa: E402
from db.import_json import import_data  # noqa: E402


def setup():
    if not database_path().exists():
        import_data()
    with connection() as conn:
        conn.executescript((ROOT / "sql" / "accounts.sql").read_text(encoding="utf-8"))
        if conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0:
            password = secrets.token_urlsafe(15)
            access = ROOT / "data" / "local-access.txt"
            access.write_text(
                "Локальная учетная запись редактора\n"
                f"Логин: museum\nПароль: {password}\n"
                "Вход: http://127.0.0.1:8000/accounts/login/\n"
                "Этот файл не публиковать и не включать в отчеты.\n",
                encoding="utf-8",
            )
            with conn:
                conn.execute(
                    "INSERT INTO accounts (username, password_hash, role) "
                    "VALUES (?, ?, ?)", ("museum", make_password(password), "editor"),
                )
    key = ROOT / ".secret-key"
    if not key.exists():
        key.write_text(secrets.token_urlsafe(60), encoding="utf-8")
    Path(ROOT / "logs").mkdir(exist_ok=True)
    print("Локальная установка готова. Данные входа: data/local-access.txt")


if __name__ == "__main__":
    setup()

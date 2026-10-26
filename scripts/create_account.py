import argparse
import getpass
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum_site.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth.hashers import make_password  # noqa: E402
from db.database import connection  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Создать учетную запись")
    parser.add_argument("username")
    parser.add_argument("--role", choices=["editor", "viewer"], default="viewer")
    args = parser.parse_args()
    password = getpass.getpass("Пароль (не менее 12 символов): ")
    if len(password) < 12 or password != getpass.getpass("Повторите пароль: "):
        parser.error("Пароли должны совпадать и содержать не менее 12 символов.")
    with connection() as conn, conn:
        conn.execute(
            "INSERT INTO accounts (username, password_hash, role) VALUES (?, ?, ?)",
            (args.username, make_password(password), args.role),
        )
    print("Учетная запись создана.")

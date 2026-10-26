"""Локальное развертывание: python run_local.py (порт 8000)."""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum_site.deploy")

from waitress import serve  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402

if __name__ == "__main__":
    print("Музей: http://127.0.0.1:8000/ (Ctrl+C для остановки)")
    serve(get_wsgi_application(), host="127.0.0.1", port=8000, threads=4)

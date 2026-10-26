from .settings import *  # noqa: F403,F401
from .settings import BASE_DIR

DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
SECRET_KEY = (BASE_DIR / ".secret-key").read_text(encoding="utf-8").strip()
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "homepage.operations.RequestLogMiddleware",
]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

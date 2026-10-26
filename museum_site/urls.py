from django.urls import include, path

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("api/", include("api.urls")),
    path("", include("homepage.urls")),
    path("halls/", include("halls.urls")),
    path("exhibitions/", include("exhibitions.urls")),
]
handler404 = "homepage.views.not_found"

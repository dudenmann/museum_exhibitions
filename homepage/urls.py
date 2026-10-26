from django.urls import path

from . import views, operations

app_name = "homepage"
urlpatterns = [
    path("health/", operations.health, name="health"),
    path("workspace/", operations.workspace, name="workspace"),
    path("", views.index, name="index"),
    path("curators/", views.curators, name="curators"),
    path("statistics/", views.statistics, name="statistics"),
]

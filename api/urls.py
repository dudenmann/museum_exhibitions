from django.urls import path
from . import views

app_name = "api"
urlpatterns = [
    path("exhibitions/", views.exhibitions, name="exhibitions"),
    path("exhibitions/<int:item_id>/", views.exhibition_detail, name="detail"),
    path("halls/", views.halls, name="halls"),
    path("curators/", views.curators, name="curators"),
]

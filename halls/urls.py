from django.urls import path

from . import views

app_name = "halls"
urlpatterns = [
    path("", views.index, name="list"),
    path("available/", views.available, name="available"),
    path("<int:item_id>/", views.detail, name="detail"),
]

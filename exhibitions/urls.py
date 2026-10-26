from django.urls import path

from . import views

app_name = "exhibitions"
urlpatterns = [
    path("", views.index, name="list"),
    path("<int:item_id>/", views.detail, name="detail"),
]

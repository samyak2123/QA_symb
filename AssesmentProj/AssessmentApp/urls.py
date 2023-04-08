from django.urls import path
from . import views

urlpatterns = [
    path("startapp/", views.welcome),
    path("startapp/back", views.validate),
]
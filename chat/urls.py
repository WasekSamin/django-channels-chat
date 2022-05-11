from django.urls import path

from .views import *

app_name = "chat"
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
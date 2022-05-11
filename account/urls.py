from django.urls import path

from .views import *

app_name = "account"
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("create-account/", CreateAccountView.as_view(), name="create-account"),
    path("user-login/", UserLoginView.as_view(), name="user-login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
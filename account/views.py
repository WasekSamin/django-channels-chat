from django.shortcuts import redirect, render
from django.views import View
from django.http import JsonResponse
from .models import Account
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from core.find_object import find_obj


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("chat:home")
        return render(request, "account/register.html")


class CreateAccountView(View):
    def post(self, request):
        username = request.POST.get("username", None)
        email = request.POST.get("email", None)
        password = request.POST.get("password", None)

        json_resp = {"error": True}

        if username is not None and email is not None and password is not None:
            accounts = Account.objects.values()
            account_list = list(map(lambda i: i, accounts))

            account_obj = find_obj(account_list, "email", email, 0, len(account_list))

            if account_obj is not None:
                json_resp = {
                    "error": False,
                    "user_exist": True
                }
            else:
                user = Account(
                    username=username,
                    email=email,
                    password=make_password(password)
                )
                user.save()

                login(request, user)

                json_resp = {
                    "error": False,
                    "user_created": True
                }

        return JsonResponse(json_resp, safe=False)

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("chat:home")
        return render(request, "account/login.html")


class UserLoginView(View):
    def post(self, request):
        email = request.POST.get("email", None)
        password = request.POST.get("password", None)

        json_resp = {"error": True}

        if email is not None and password is not None:
            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)

                json_resp = {
                    "error": False,
                    "user_login": True
                }
            else:
                json_resp = {
                    "error": False,
                    "invalid_user": True
                }

        return JsonResponse(json_resp, safe=False)


class LogoutView(View):
    def get(self, request):
        logout(request)

        return redirect("account:login")
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from account.models import *

# Create your views here.

class HomeView(LoginRequiredMixin, View):
    login_url = '/account/login/'
    def get(self, request):
        accounts = Account.objects.values()

        args = {
            "accounts": accounts
        }
        return render(request, "chat/home.html", args)
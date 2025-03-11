from django.shortcuts import redirect
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def logout(self, request):
        super().logout(request)
        return redirect("home:index")

from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect

class CustomAccountAdapter(DefaultAccountAdapter):
    
    def logout(self, request):

        super().logout(request)
        
        return redirect('home')
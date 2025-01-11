from django.shortcuts import render

def profile_home(request):

    return render(request, 'profiles/profile_home.html')
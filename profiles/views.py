from django.shortcuts import render
from profiles.models import UserProfile

def profile_home(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "profiles/profiles_home.html", {"profile": profile})

def profile_edit(request):
    return render(request, "profiles/profile_edit.html")
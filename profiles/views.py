
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm

def profile_home(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "profiles/profiles_home.html", {"profile": profile})

def profile_edit(request):
    return render(request, "profiles/profile_edit.html")

@login_required
def profile_edit(request):
    # Get or create the user's profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profiles:home')  # Redirect to your profile details/home page
    else:
        form = UserProfileForm(instance=profile)
        
    return render(request, "profiles/profile_edit.html", {'form': form})

@login_required
def profile_home(request):
    # Get or create the user's profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    # Get all orders linked to this profile, ordered by most recent
    orders = profile.orders.all().order_by('-date')
    
    context = {
        'profile': profile,
        'orders': orders,
    }
    return render(request, "profiles/profiles_home.html", context)


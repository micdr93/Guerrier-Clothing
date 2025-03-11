from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm


@login_required
def profile_home(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    orders = (
        profile.orders.all().order_by("-date") if hasattr(profile, "orders") else []
    )
    context = {"profile": profile, "orders": orders}
    return render(request, "profiles/profiles_home.html", context)


@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            full_name = form.cleaned_data.get("full_name")
            email = form.cleaned_data.get("email")
            if full_name:
                request.user.first_name = full_name
                request.user.save()
            if email:
                request.user.email = email
                request.user.save()
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profiles:home")
    else:
        initial_data = {
            "full_name": request.user.first_name or "",
            "email": request.user.email or "",
        }
        form = UserProfileForm(instance=profile, initial=initial_data)
    return render(request, "profiles/profile_edit.html", {"form": form})

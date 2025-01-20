
from django.shortcuts import render
from .forms import ProductForm, ReviewsForm
from .models import Product, Category, Reviews
from django.http import HttpResponse



from profiles.models import UserProfile


def profile_home(request):
    return HttpResponse("Profile Home Page")

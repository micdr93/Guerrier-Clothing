from django.shortcuts import render

from django.shortcuts import render

def wishlist_home(request):
  
    return render(request, 'wishlist/wishlist_home.html')
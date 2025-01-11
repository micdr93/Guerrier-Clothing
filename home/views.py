from django.shortcuts import render

# Create your views here.

def index(request):

    return render(request, 'home/index.html')

def privacy_policy(request):

    return render(request, 'privacy_policy.html')

def returns(request):

    return render(request, 'returns.html')

def contact(request):
    
    return render(request, 'contact.html')
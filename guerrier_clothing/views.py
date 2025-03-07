from django.shortcuts import render

from products.models import Product 

def index(request):
    products = Product.objects.all()  
    context = {
        'products': products 
    }
    return render(request, 'index.html', context)


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request,'errors/500.html', status=500)


def products_view(request):
    """A view to show all products"""
    products = Product.objects.filter(is_active=True)
    
    context = {
        'products': products,
    }
    
    return render(request, 'home/products.html', context)
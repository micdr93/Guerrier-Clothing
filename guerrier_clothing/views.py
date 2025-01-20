from django.shortcuts import render

from products.models import Product 

def index(request):
    products = Product.objects.all()  
    context = {
        'products': products 
    }
    return render(request, 'index.html', context)


def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)


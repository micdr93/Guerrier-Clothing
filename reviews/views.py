from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.models import Product
from .forms import ReviewForm

@login_required
def add_review(request, product_id):
    # Get the product
    product = get_object_or_404(Product, pk=product_id)

    # Check if the user has already submitted a review
    if product.reviews.filter(user=request.user).exists():
        messages.info(request, "You have already reviewed this product.")
        return redirect('products:product_detail', product_id=product.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
           
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
          
            review.save()
            messages.success(request, "Your review was submitted successfully!")
            return redirect('products:product_detail', product_id=product.id)
        else:
            messages.error(request, "There were errors with your submission.")
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'reviews/add_review.html', context)

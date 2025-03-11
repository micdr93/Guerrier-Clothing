from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from products.models import Product
from .forms import ReviewForm
from .models import Review


@login_required
def add_review(request, product_id):
    # Get the product
    product = get_object_or_404(Product, pk=product_id)

    # Check if the user has already submitted a review
    if product.reviews.filter(user=request.user).exists():
        messages.info(request, "You have already reviewed this product.")
        return redirect("products:product_detail", product_id=product.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Use a transaction to ensure everything completes properly
            with transaction.atomic():
                review = form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()

                # Force a refresh of the product from the database after rating update
                product.refresh_from_db()

            messages.success(request, "Your review was submitted successfully!")
            # Add a query parameter to prevent caching
            return redirect(f"/products/{product.id}/?review_added=true")
        else:
            messages.error(request, "There were errors with your submission.")
    else:
        form = ReviewForm()

    context = {
        "form": form,
        "product": product,
    }
    return render(request, "reviews/add_review.html", context)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)

    # Check if the user is the owner or a superuser
    if request.user == review.user or request.user.is_superuser:
        product_id = review.product.id

        # Use a transaction for deleting to ensure updates happen properly
        with transaction.atomic():
            review.delete()
            # Get a fresh product instance and update rating
            product = Product.objects.get(pk=product_id)
            product.update_rating()

        messages.success(request, "Review deleted successfully.")
        # Add a query parameter to prevent caching
        return redirect(f"/products/{product_id}/?review_deleted=true")
    else:
        messages.error(request, "You don't have permission to delete this review.")
        return redirect("products:product_detail", product_id=review.product.id)


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.user != review.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit this review.")
        return redirect("products:product_detail", product_id=review.product.id)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated!")
            return redirect("products:product_detail", product_id=review.product.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, "reviews/edit_review.html", {"form": form, "review": review})

from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Review
from products.models import Product
from .forms import ReviewForm

@login_required
def add_review(request, product_id):
    """Add a review for a product"""
    product = get_object_or_404(Product, pk=product_id)
    existing_review = Review.objects.filter(product=product, user=request.user).first()
    if existing_review:
        messages.info(
            request,
            "You've already reviewed this product. You can edit your review instead.",
        )
        return redirect(reverse("products:product_detail", args=[product_id]))

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Review added successfully!")
            return redirect(reverse("products:product_detail", args=[product_id]) + "?review_added=True")
    else:
        form = ReviewForm()

    context = {
        "form": form,
        "product": product,
    }
    return render(request, "reviews/add_review.html", context)

@login_required
def update_review(request, review_id):
    """Update a review"""
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit this review.")
        return redirect(reverse("products:product_detail", args=[review.product.id]))

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully!")
            return redirect(reverse("products:product_detail", args=[review.product.id]) + "?review_added=True")
    else:
        form = ReviewForm(instance=review)

    context = {
        "form": form,
        "review": review,
        "product": review.product,
    }
    return render(request, "reviews/edit_review.html", context)

@login_required
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, pk=review_id)
    product_id = review.product.id

    if review.user != request.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete this review.")
        return redirect(reverse("products:product_detail", args=[product_id]))

    if request.method == "POST":
        review.delete()
        messages.success(request, "Review deleted successfully!")
        return redirect(reverse("products:product_detail", args=[product_id]) + "?review_deleted=True")

    context = {
        "review": review,
        "product": review.product,
    }
    return render(request, "reviews/delete_review.html", context)

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["title", "review", "rating"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Review title", "class": "form-control"}
            ),
            "review": forms.Textarea(
                attrs={"placeholder": "Write your review here", "class": "form-control"}
            ),
            "rating": forms.NumberInput(
                attrs={"min": 1, "max": 5, "class": "form-control"}
            ),
        }

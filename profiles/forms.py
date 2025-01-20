from django import forms
from .models import UserProfile


class ProductForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = '__all__'

class ReviewsForm(forms.Form):
        title = forms.CharField(max_length=100)
        content = forms.CharField(widget=forms.Textarea)
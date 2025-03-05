from django import forms
from .models import Contact
from .models import Product
from .models import Category 
from .models import NewsletterSubscription
from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact  
        fields = ['name', 'email', 'message'] 
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product 
        fields = ['name', 'description', 'price', 'stock']

class CategoryForm(forms.ModelForm):
     class Meta:
        model = Category
        fields = ['name', 'description']


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'})
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
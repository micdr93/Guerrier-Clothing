from django import forms
from .models import Contact
from .models import Product
from .models import Category


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
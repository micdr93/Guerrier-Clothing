from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category, Reviews


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    image = forms.ImageField(label='Image', required=False, widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'


class ReviewsForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ["title", "review"]

    title = forms.CharField(max_length=100, required=True)
    review = forms.CharField(max_length=1500, required=True)
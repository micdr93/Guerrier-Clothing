from django import forms
from .models import UserProfile

class ProductForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'

class ReviewsForm(forms.Form):
    title = forms.CharField(max_length=100)
    content = forms.CharField(widget=forms.Textarea)

class UserProfileForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = UserProfile
        exclude = ('user',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
        }

        for field in self.fields:
            if field != 'default_country':
                if self.fields[field].required:
                    placeholder = f'{placeholders.get(field, field)} *'
                else:
                    placeholder = placeholders.get(field, field)
                self.fields[field].widget.attrs['placeholder'] = placeholder
            
            self.fields[field].widget.attrs['class'] = 'border-black rounded-0 profile-form-input'
            self.fields[field].label = False
from django import forms
from eshop.accounts.models import Shopper, ShippingAddress


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = Shopper
        fields = ["email","last_name", "first_name", "date_birth", "password"]



class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ["name", "address_1", "address_2", "city", "district", "zip_code"]
from django import forms
from eshop.accounts.models import Shopper


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = Shopper
        fields = ["email","last_name", "first_name", "date_birth", "password"]
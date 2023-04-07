from django import forms
from .models import Customer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserForm(UserCreationForm):

    first_name = forms.CharField(max_length=140, required=True)
    last_name = forms.CharField(max_length=140, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2','first_name', 'last_name', 'email', 'is_active']


class CustomerForm(forms.ModelForm):

    name = forms.CharField(max_length=140, required=True)
    name = forms.CharField( required=True)

    class Meta:
        model = Customer
        fields = ['name', 'phone' ]
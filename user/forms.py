from django import forms
from .models import Customer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']


class CustomerForm(forms.ModelForm):

    name = forms.CharField(max_length=140, required=True)
    name = forms.CharField( required=True)

    class Meta:
        model = Customer
        fields = ['name', 'phone' ]
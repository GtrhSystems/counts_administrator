from django import forms
from .models import Customer
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.contrib.auth.models import User, Permission

PERMISSIONS_ACTIVES = [
    'change_platform',
    'add_customer',
    'change_customer',
    'add_user',
    'add_count',
    'change_count',
    'delete_count',
    'change_count',
    'add_promotion',
    'delete_sale',
    'add_sale',
    'add_plan',
    'change_plan',
    'delete_customer'
]

class UserForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']


class CustomerForm(forms.ModelForm):

    name = forms.CharField(max_length=140, required=True)
    phone = forms.CharField( required=True)

    class Meta:
        model = Customer
        fields = ['name', 'phone' ]

class CustomUserChangeForm(UserChangeForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(codename__in=PERMISSIONS_ACTIVES),
        widget=forms.SelectMultiple,
        required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_login', 'user_permissions', 'last_name', 'email', 'password1', 'password2','is_active', 'is_staff']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserCreationForm(UserCreationForm):

    user_permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.filter(codename__in=PERMISSIONS_ACTIVES),
                                              widget=forms.SelectMultiple,
                                              required=False )
    class Meta:
        model = User
        fields = ['username', 'last_login', 'first_name', 'user_permissions',  'last_name', 'email', 'password1', 'password2']
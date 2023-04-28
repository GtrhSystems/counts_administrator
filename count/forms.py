from django import forms
from .models import Sale, Platform, Count, Promotion
import datetime

class SaleForm(forms.Form):

    def __init__(self, *args, **kwargs):

        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['platform'] = forms.ModelChoiceField(queryset=Platform.get_my_platforms_whit_counts(), required=True, label="Plataforma")
        self.fields['months'] = forms.IntegerField(label="Meses", required=True,)


class RenovationForm(forms.Form):


    months = forms.IntegerField(label="Meses", required=True,)


class GetInterDatesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        from datetime import date
        super(GetInterDatesForm, self).__init__(*args, **kwargs)
        self.fields['init_date'] = forms.DateField(widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': 'Digite la fecha inicial', 'data-date-format': 'YYYY/MMMM/DD',
                   'value': date.today()}))
        self.fields['final_date'] = forms.DateField(widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': 'Digite la fecha final', 'data-date-format': 'YYYY/MMMM/DD',
                   'value': date.today()}))

    class Meta:
        fields = ('init_date', 'final_date')

class CountForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(CountForm, self).__init__(*args, **kwargs)
        platforms = Platform.objects.filter(active=True)
        self.fields['platform'] = forms.ModelChoiceField(queryset=platforms, help_text='Selecciones la plataforma',
                                                      label="Plataforma")

    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, label="Contraseña")

    def save(self, commit=True):

        instance = super().save(commit=False)


        super(CountForm, self).save(*args, **kwargs)

class CreatePromotionForm(forms.ModelForm):

    class Meta:
        model = Promotion
        fields = ["name", "price", "date_init", "date_finish", "active", "image"]


class CreatePlatformForm(forms.ModelForm):

    class Meta:
        model = Platform
        fields = ["name", "active", "logo", "num_profiles", "price"]


class PlatformForm(forms.Form):

    platforms = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())

    class Meta:
        fields = ["platforms"]

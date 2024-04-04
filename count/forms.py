from django import forms
from .models import Sale, Platform, Count, Promotion

from datetime import date

class SaleForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['platform'] = forms.ModelChoiceField(queryset=Platform.get_my_platforms_with_counts(), required=True, label="Plataforma")
        self.fields['months'] = forms.IntegerField(min_value=1 ,label="Meses", required=True)



class RenovationForm(forms.Form):


    months = forms.IntegerField(label="Meses", required=True, widget= forms.NumberInput(attrs={'placeholder':'Ingrese los meses', 'min':'1'}))


class GetInterDatesForm(forms.Form):

    def __init__(self, *args, **kwargs):

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
        self.fields['date_limit'] = forms.DateField(label="Fecha de vencimiento",  widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': 'Digite la fecha de vencimiento', 'data-date-format': 'YYYY/MMMM/DD',
                   'value': date.today()}))

    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, label="Contraseña")

    def save(self, commit=True):

        instance = super().save(commit=False)
        super(CountForm, self).save(*args, **kwargs)


class ChangeCountDataForm(forms.Form):

    pin = forms.CharField(required=False, label="Pin")
    password = forms.CharField(required=False, label="Contraseña")


class ChangeSaleDataForm(forms.Form):

     def __init__(self, id,  *args, **kwargs):

        super(ChangeSaleDataForm, self).__init__(*args, **kwargs)
        sale = Sale.objects.filter(id=id).first()
        self.fields['date'] = forms.DateField(widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': 'Fecha de venta', 'data-date-format': 'YYYY/MMMM/DD',
                   'value': sale.date}))
        self.fields['date_limit'] = forms.DateField(widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': 'Fecha de finalización', 'data-date-format': 'YYYY/MMMM/DD',
                   'value': sale.date_limit}))




class ChangePaswordForm(forms.ModelForm):
    class Meta:
        model = Count
        fields = ["password"]

class ChangePaswordEmailForm(ChangePaswordForm):

    class Meta(ChangePaswordForm.Meta):
        fields = ['email_password']


class SearchCountForm(forms.ModelForm):
    class Meta:
        model = Count
        fields = ["email", "platform"]


class ChangeDatePaswordForm(forms.ModelForm):
    class Meta:
        model = Count
        fields = ["password", 'date_limit']



class ChangeDateLimitForm(forms.ModelForm):

    class Meta:
        model = Count
        fields = ["date_limit"]


class CreatePromotionForm(forms.ModelForm):

    class Meta:
        model = Promotion
        fields = ["name", "price", "date_init", "date_finish", "active", "image"]


class CreatePlatformForm(forms.ModelForm):

    class Meta:
        model = Platform
        fields = ["name", "active", "logo", "num_profiles"]


class PlatformForm(forms.Form):

    platforms = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())

    class Meta:
        fields = ["platforms"]

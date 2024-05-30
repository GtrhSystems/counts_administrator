from django import forms
from .models import Sale, Platform, Plan, Count, Promotion, Country

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
        self.fields['platform'] = forms.ModelChoiceField(queryset=platforms, empty_label='Selecciones la plataforma',
                                                      label="Plataforma")
        countries = Country.objects.all()
        self.fields['country'] = forms.ModelChoiceField(queryset=countries, empty_label='Selecciones el pais',
                                                         label="Pais")
        self.fields['country'].initial = 1

        self.fields['date_limit'] = forms.DateField(label="Fecha de vencimiento",  widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': 'Digite la fecha de vencimiento', 'data-date-format': 'YYYY/MMMM/DD',
                   'value': date.today()}))

    email = forms.CharField(required=True)
    password = forms.CharField(required=True, label="Contraseña de cuenta")
    email_password = forms.CharField(required=True, label="Contraseña de email")



    def save(self, commit=True):

        instance = super().save(commit=False)
        super(CountForm, self).save(*args, **kwargs)


class CountUpdateForm(forms.ModelForm):
    class Meta:
        model = Count
        fields = ['platform', 'country', 'email', 'date_limit']


class CountPlanForm(forms.Form):

    def __init__(self, platform_id, *args, **kwargs):

        super(CountPlanForm, self).__init__(*args, **kwargs)
        plans = Plan.objects.filter(platform_id=platform_id, active=True)
        if len(plans) > 0:
            self.fields['plan'] = forms.ModelChoiceField(queryset=plans, help_text='Selecciones el plan',  label="Plan")
        else:
            self.fields['plan'] = None




class PlanForm(forms.ModelForm):

    def __init__(self, platform, *args, **kwargs):
        super(PlanForm, self).__init__(*args, **kwargs)
        self.fields['num_profiles'] = forms.IntegerField(label="Perfiles a vender", widget=forms.NumberInput(
            attrs={'min': 1, 'max': platform.num_profiles,  'placeholder': 'Digite el numero de perfiles a vender en este plan'}))
    class Meta:
        model = Plan
        fields = [ 'name', 'num_profiles', 'active', 'description']


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

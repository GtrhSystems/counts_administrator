from django import forms
from .models import Sale, Platform

class SaleForm(forms.Form):

    def __init__(self, *args, **kwargs):

        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['platform'] = forms.ModelChoiceField(queryset=Platform.get_my_platforms_whit_counts(), required=True, label="Plataforma")
        self.fields['months'] = forms.IntegerField(label="Meses", required=True,)

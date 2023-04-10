from django import forms
from .models import Sale, Platform
import datetime

class SaleForm(forms.Form):

    def __init__(self, *args, **kwargs):

        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['platform'] = forms.ModelChoiceField(queryset=Platform.get_my_platforms_whit_counts(), required=True, label="Plataforma")
        self.fields['months'] = forms.IntegerField(label="Meses", required=True,)


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

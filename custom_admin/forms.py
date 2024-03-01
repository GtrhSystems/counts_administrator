from django import forms
from user.models import  UserTwoFactorAuthData
from django.core.exceptions import ValidationError

class OTPForm(forms.Form):

    otp = forms.CharField(required=True, label="Ingrese en número OTP")

    def clean_otp(self):

        self.two_factor_auth_data = UserTwoFactorAuthData.objects.filter(
            user=self.user
        ).first()
        if self.two_factor_auth_data is None:
            raise ValidationError('2FA no configurado.')
        otp = self.cleaned_data.get('otp')
        if not self.two_factor_auth_data.validate_otp(otp):
            raise ValidationError('Código 2FA inválido.')
        return otp
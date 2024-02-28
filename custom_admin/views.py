from django.views.generic import TemplateView, FormView
from user.libraries import user_two_factor_auth_data_create
from user.models import UserTwoFactorAuthData
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django import forms
import pyotp


class AdminSetupTwoFactorAuthView(TemplateView):

    template_name = "admin_2fa/setup_2fa.html"
    def post(self, request):
        print("esta entrando por el hgp admin no se opr que hps")
        context = {}
        try:
            two_factor_auth_data = user_two_factor_auth_data_create(user=request.user)
            context["otp_secret"] = two_factor_auth_data.otp_secret
            context["qr_code"] = two_factor_auth_data.generate_qr_code(name=request.user.email)
        except ValidationError as exc:
            context["form_errors"] = exc.messages

        return self.render_to_response(context)

class AdminConfirmTwoFactorAuthView(FormView):
    template_name = "admin_2fa/confirm_2fa.html"
    success_url = reverse_lazy("admin:index")

    class Form(forms.Form):
        
        otp = forms.CharField(required=True)

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

    def get_form_class(self):

        return self.Form

    def get_form(self, *args, **kwargs):

        form = super().get_form(*args, **kwargs)
        form.user = self.request.user
        return form

    def form_valid(self, form):

        form.two_factor_auth_data.rotate_session_identifier()
        self.request.session['2fa_token'] = str(form.two_factor_auth_data.session_identifier)
        return super().form_valid(form)
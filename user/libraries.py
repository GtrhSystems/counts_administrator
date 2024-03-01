from django.core.exceptions import ValidationError
import pyotp
from .models import UserTwoFactorAuthData

def user_two_factor_auth_data_create(*, user) -> UserTwoFactorAuthData:

    if hasattr(user, 'two_factor_auth_data'):
        raise ValidationError(
            'No puede tener más de un dato relacionado con 2FA.'
        )

    two_factor_auth_data = UserTwoFactorAuthData.objects.create(
        user=user,
        otp_secret=pyotp.random_base32()
    )
    return two_factor_auth_data
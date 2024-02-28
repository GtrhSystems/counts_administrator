from django.db import models
from phonenumber_field.modelfields import PhoneNumberField# pip install "django-phonenumber-field[phonenumberslite]"
from count.libraries import getDifference
from django.contrib.auth.models import User
import datetime
from typing import Optional
import pyotp
import qrcode
import qrcode.image.svg
import uuid


class Customer(models.Model):

    name =  models.CharField( max_length=100, verbose_name="Nombres")
    #devices = models.PositiveIntegerField(default=0, verbose_name="Dispositivos")
    phone = PhoneNumberField(null=False, blank=False, unique=False, verbose_name="Telfono")
    active = models.BooleanField( default=1, verbose_name="Activado")

    @classmethod
    def is_valid(cls, id):

        exist = True if cls.objects.filter(id=id).first() else False
        return exist

    @classmethod
    def get_phones_for_messages(cls, Sale):

        now = datetime.datetime.now(datetime.timezone.utc)
        today = datetime.date.today()
        yestarday = today + datetime.timedelta(days=-1)
        tomorrow = today + datetime.timedelta(days=1)
        date_ago = today + datetime.timedelta(days=2)
        end_date_ago = date_ago + datetime.timedelta(days=1)
        payload = {}

        sales_today = Sale.objects.filter(date_limit__gte=today, date_limit__lt=tomorrow, renovated=False)
        sales_yesterday = Sale.objects.filter(date_limit__gte=yestarday, date_limit__lt=today, renovated=False)
        sales_3_days = Sale.objects.filter(date_limit__gte=date_ago, date_limit__lt=end_date_ago, renovated=False)
        sales = sales_yesterday | sales_today | sales_3_days

        for sale in sales:

            remaining_days = getDifference(sale.date_limit, now, "days")
            if remaining_days == 1:
                day = "vencio ayer"
            elif remaining_days == 0:
                day = "vence hoy"
            elif remaining_days == -2:
                day = "vence en dos dias"

            payload[sale.profile.count.email + sale.bill.customer.name] = { "name": sale.bill.customer.name,
                             "email": sale.profile.count.email,
                             "password": sale.profile.count.password,
                             "phone":sale.bill.customer.phone.as_e164,
                             "platform":  sale.profile.count.platform,
                             "days" :  day
                             }
        return payload


class Action(models.Model):

    user = models.ForeignKey(User, verbose_name="Vendedor", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    action = models.CharField( max_length=250, verbose_name="Accion")

    @classmethod
    def action_register(cls, user, action):
        print(user)
        print(action)

        cls.objects.create(user=user, action=action)


class UserTwoFactorAuthData(models.Model):

    user = models.OneToOneField(User, related_name='two_factor_auth_data', on_delete=models.CASCADE)
    otp_secret = models.CharField(max_length=255)
    session_identifier = models.UUIDField(blank=True, null=True)

    def generate_qr_code(self, name: Optional[str] = None) -> str:

        totp = pyotp.TOTP(self.otp_secret)
        qr_uri = totp.provisioning_uri(
            name=name,
            issuer_name='El Gamer Mexicano 2FA'
        )

        image_factory = qrcode.image.svg.SvgPathImage
        qr_code_image = qrcode.make(
            qr_uri,
            image_factory=image_factory
        )

        # The result is going to be an HTML <svg> tag
        return qr_code_image.to_string().decode('utf_8')

    def validate_otp(self, otp: str) -> bool:

        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(otp)

    def rotate_session_identifier(self):

        self.session_identifier = uuid.uuid4()
        self.save(update_fields=["session_identifier"])
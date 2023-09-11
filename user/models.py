from django.db import models
from phonenumber_field.modelfields import PhoneNumberField# pip install "django-phonenumber-field[phonenumberslite]"
from count.libraries import getDifference
from django.contrib.auth.models import User
import datetime


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

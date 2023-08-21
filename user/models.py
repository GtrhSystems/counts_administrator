from django.db import models
from phonenumber_field.modelfields import PhoneNumberField# pip install "django-phonenumber-field[phonenumberslite]"
from count.libraries import getDifference
from django.contrib.auth.models import User

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
    def get_phones_for_messages(cls, Sale, now, date_ago):

        payload = []
        sales = Sale.objects.filter(date_limit__range=[now, date_ago ]).order_by('-date')
        for sale in sales:
            remaining_days = getDifference(sale.date_limit, now, "days")
            payload.append({ "email": sale.profile.count.email,
                             "password": sale.profile.count.password,
                             "phone":sale.bill.customer.phone.as_e164,
                             "remaining_days":  abs(remaining_days) })
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

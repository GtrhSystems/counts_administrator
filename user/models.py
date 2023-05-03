from django.db import models
from phonenumber_field.modelfields import PhoneNumberField# pip install "django-phonenumber-field[phonenumberslite]"
from count.libraries import getDifference


class Customer(models.Model):

    name =  models.CharField( max_length=20, verbose_name="Nombres")
    #devices = models.PositiveIntegerField(default=0, verbose_name="Dispositivos")
    phone = PhoneNumberField(null=False, blank=False, unique=True, verbose_name="Telefono")
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
                             "phone":sale.customer.phone.as_e164,
                             "remaining_days":  abs(remaining_days) })
        return payload


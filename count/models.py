from django.db import models
from .validators import valid_extension, valid_image_extension
from user.models import Customer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from count.libraries import CalculateDateLimit
from datetime import datetime , timedelta

class Platform(models.Model):

    name = models.CharField(max_length=150, verbose_name="Nombre", default="")
    active = models.BooleanField(default=1, verbose_name="Activo?:")
    logo =  models.FileField(default="", upload_to='logos', validators=[valid_image_extension])
    num_profiles = models.IntegerField(default=1)
    price = models.FloatField(default=0)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Plataforma'
        verbose_name_plural = 'Plataformas'

    @classmethod
    def get_my_platforms_whit_counts(self):

        platforms = self.objects.all()

        for platform in platforms:
            have_counts = True if Profile.objects.filter(count__platform=platform, saled=0) else False
            if not have_counts:
                platforms = platforms.exclude(id=platform.id)
        return platforms


class Count(models.Model):

    platform = models.ForeignKey(Platform, verbose_name="Plataforma", on_delete=models.CASCADE)
    email = models.CharField(max_length=100, verbose_name="Email")
    password = models.CharField(max_length=50, default="")
    pin = models.CharField(max_length=4, verbose_name="Pin", default="0")

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'



class Profile(models.Model):

    count = models.ForeignKey(Count, verbose_name="Plataforma", on_delete=models.CASCADE)
    profile = models.CharField(max_length=100, verbose_name="Perfil")
    saled = models.BooleanField(default=0, verbose_name="Vendida?:")

    @receiver(post_save, sender=Count, dispatch_uid="creaction_of_profiles_by_count")
    def create_profiles(sender, instance, **kwargs):

        num_profiles = instance.platform.num_profiles
        for profile in range(num_profiles):
            Profile.objects.create(count=instance, profile=profile )
        return None

    @classmethod
    def search_profile_no_saled(cls, platform):

        profile = cls.objects.filter(saled=0, count__platform=platform).first()
        return profile

class Sale(models.Model):

    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, verbose_name="Cliente", on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="Perfil")
    price = models.FloatField(default=0)
    months = models.PositiveIntegerField(default=1)
    date_limit = models.DateTimeField(verbose_name="Fecha de vencimiento", blank=True, null=True, auto_now_add=False)
    saler = models.ForeignKey(User, verbose_name="Vendedor", on_delete=models.CASCADE)

    @classmethod
    def GetInterdatesSales(cls, user, initial_date, final_date):

        initial_date = datetime.strptime(initial_date, '%Y-%m-%d')
        final_date = datetime.strptime(final_date, '%Y-%m-%d')
        initial_date = initial_date + timedelta(hours=5)
        final_date = final_date + timedelta(hours=29)
        sales = cls.objects.filter(saler=user, date__range=[initial_date, final_date]).order_by(
                '-date')
        return sales





def sale_profile(self, customer, profile, months):

    date_limit = CalculateDateLimit(months)
    Sale.objects.create(customer = customer,
                        profile = profile,
                        price = profile.count.platform.price * months,
                        months = months,
                        date_limit = date_limit,
                        saler = self)
    profile.saled = True
    profile.save()
    return profile.count

User.add_to_class("sale_profile", sale_profile)
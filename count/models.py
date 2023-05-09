from django.db import models
from .validators import valid_extension, valid_image_extension
from user.models import Customer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User




class Platform(models.Model):

    name = models.CharField(max_length=150, verbose_name="Nombre", default="")
    active = models.BooleanField(default=1, verbose_name="Activo?:")
    logo =  models.FileField(default="", upload_to='logos', validators=[valid_image_extension])
    num_profiles = models.IntegerField(default=0, verbose_name="Número de perfiles")
    #price = models.FloatField(default=0, verbose_name="Precio")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Plataforma'
        verbose_name_plural = 'Plataformas'

    @classmethod
    def get_my_platforms_with_counts(cls):

        platforms = cls.objects.all()

        for platform in platforms:
            have_counts = True if Profile.objects.filter(count__platform=platform, saled=0) else False
            if not have_counts:
                platforms = platforms.exclude(id=platform.id)
        return platforms

    @classmethod
    def get_num_of_profiles(cls, platform_id):

        platform = Platform.objects.filter(id=platform_id).first()
        return platform.num_profiles

class Price(models.Model):

    platform = models.ForeignKey(Platform, verbose_name="Plataforma", on_delete=models.CASCADE)
    num_profiles = models.PositiveIntegerField( verbose_name="Número de perfiles")
    price = models.FloatField(default=0, verbose_name="Precio")


class Count(models.Model):

    platform = models.ForeignKey(Platform, verbose_name="Plataforma", on_delete=models.CASCADE)
    email = models.CharField(max_length=100, verbose_name="Email")
    password = models.CharField(max_length=50, default="")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'


class Promotion(models.Model):

    name = models.CharField(max_length=150, default="", verbose_name="Nombre")
    price = models.FloatField(max_length=10, verbose_name="Precio")
    date_init = models.DateTimeField(verbose_name="Fecha de Inicio",  auto_now_add=False)
    date_finish = models.DateTimeField(verbose_name="Fecha de Finalización", auto_now_add=False)
    active = models.BooleanField(default=1, verbose_name="Activo?:")
    creater = models.ForeignKey(User, verbose_name="Creador", on_delete=models.CASCADE)
    image = models.FileField(default="", upload_to='promotions', validators=[valid_image_extension])

    class Meta:
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'



class PromotionPlatform(models.Model):

    promotion = models.ForeignKey(Promotion, verbose_name="Promoción", on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, verbose_name="Plataforma", on_delete=models.CASCADE)


class Profile(models.Model):

    count = models.ForeignKey(Count, verbose_name="Plataforma", on_delete=models.CASCADE)
    profile = models.CharField(max_length=100, verbose_name="Perfil")
    pin = models.CharField(max_length=4, verbose_name="Pin", default="0")
    saled = models.BooleanField(default=0, verbose_name="Vendida?:")

    #mixin
    #@receiver(post_save, sender=Count, dispatch_uid="creaction_of_profiles_by_count")
    def create_profiles(sender, instance, **kwargs):

        num_profiles = instance.platform.num_profiles
        for profile in range(num_profiles):
            Profile.objects.create(count=instance, profile=profile )
        return None

    @classmethod
    def search_profiles_no_saled(cls, platform):

        profiles = cls.objects.filter(saled=0, count__platform_id=platform)
        return profiles[:19]


class Bill(models.Model):

    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, verbose_name="Cliente", on_delete=models.CASCADE)
    saler = models.ForeignKey(User, verbose_name="Vendedor", on_delete=models.CASCADE)
    total = models.FloatField(default=0, verbose_name="Precio")

class Sale(models.Model):

    date = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="Perfil")
    months = models.PositiveIntegerField(default=1)
    date_limit = models.DateTimeField(verbose_name="Fecha de vencimiento", blank=True, null=True, auto_now_add=False)
    bill = models.ForeignKey(Bill, verbose_name="Factura", on_delete=models.CASCADE)

    @classmethod
    def GetInterdatesSales(cls, user, initial_date, final_date):

        initial_date = datetime.strptime(initial_date, '%Y-%m-%d')
        final_date = datetime.strptime(final_date, '%Y-%m-%d')
        initial_date = initial_date + timedelta(hours=5)
        final_date = final_date + timedelta(hours=29)
        sales = cls.objects.filter(saler=user, date__range=[initial_date, final_date]).order_by(
                '-date')
        return sales

    def set_renovation(self, saler, months,  CalculateDateLimit):

        date_limit = CalculateDateLimit(self.date_limit, months)
        print(self.bill.customer.name)
        post
        bill = Bill.objects.create(customer=self.bill.customer, saler=saler, total=total)
        self.objects.create(
                            months=months,
                            date_limit=date_limit,
                            bill=saler)

#facturas




def sale_profile(self, profile, months, date_limit, bill):

    profile_saled = Sale.objects.create(
                        profile = profile,
                        months = months,
                        date_limit = date_limit,
                        bill=bill
                        )
    profile.saled = True
    profile.save()
    return profile_saled

User.add_to_class("sale_profile", sale_profile)
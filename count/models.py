from django.db import models
from .validators import valid_extension, valid_image_extension
from user.models import Customer
from django.db.models.signals import post_save
from django.dispatch import receiver
from user.whatsapp_api import send_message
from django.contrib.auth.models import User
import datetime


class Platform(models.Model):

    name = models.CharField(max_length=150, verbose_name="Nombre", default="")
    active = models.BooleanField(default=1, verbose_name="Activo?:")
    logo =  models.FileField(default="", upload_to='logos/', validators=[valid_image_extension])
    num_profiles = models.IntegerField(default=0, verbose_name="Número de perfiles")
    #have_plans = models.BooleanField(default=0, verbose_name="Tiene Planes?:")
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



#Planes de cada plataforma
#SubProduct(models.Model):
class Plan(models.Model):


    platform = models.ForeignKey(Platform, default=1, verbose_name="Plataforma", on_delete=models.CASCADE)
    name = models.CharField(max_length=150, verbose_name="Nombre", default="")
    num_profiles = models.IntegerField(default=0, verbose_name="Perfiles a vender")
    have_link = models.BooleanField(default=0, verbose_name="Se envia link?:")
    active = models.BooleanField(default=1, verbose_name="Activo?:")
    description = models.CharField(default="", max_length=250, verbose_name="Descripción")

    def __str__(self):
        return str(self.name)

    @classmethod
    def get_num_of_profiles(cls, plan_id):
        plan= cls.objects.filter(id=plan_id).first()
        return plan.num_profiles


class Country(models.Model):

    country = models.CharField(default="", max_length=100, verbose_name="Pais")
    iso =  models.CharField(default="", max_length=3, verbose_name="Iso")

    class Meta:
        verbose_name = 'Pais'
        verbose_name_plural = 'paises'
        ordering = ['country']

    def __str__(self):
        return self.country


class Count(models.Model):

    platform = models.ForeignKey(Platform, verbose_name="Plataforma", on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, blank=True, null=True, verbose_name="Plan", on_delete=models.CASCADE)
    country = models.ForeignKey(Country, default=1, verbose_name="Pais", on_delete=models.CASCADE)
    email = models.CharField(max_length=100, verbose_name="Email")
    link = models.CharField(default="", max_length=130, verbose_name="Link")
    password = models.CharField(max_length=50, default="",  verbose_name="Contraseña de cuenta")
    email_password = models.CharField(max_length=50, default="", verbose_name="Contraseña de correo")
    date = models.DateTimeField(auto_now_add=True)
    date_limit = models.DateTimeField(blank=True,  null=True, verbose_name="Fecha de vencimiento",  auto_now_add=False)#Fecha de vencimiento de la cuenta

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'

    def __str__(self):
        return str(self.email)


    def change_count_password(self, new_password):

        self.password  = new_password
        self.save()

    def change_email_password(self, new_password):
        self.email_password = new_password
        self.save()



class Promotion(models.Model):

    name = models.CharField(max_length=150, default="", verbose_name="Nombre")
    price = models.FloatField(max_length=10, verbose_name="Precio")
    date_init = models.DateTimeField(verbose_name="Fecha de Inicio",  auto_now_add=False)
    date_finish = models.DateTimeField(verbose_name="Fecha de Finalización", auto_now_add=False)
    active = models.BooleanField(default=1, verbose_name="Activo?:")
    creater = models.ForeignKey(User, verbose_name="Creador", on_delete=models.CASCADE)
    image = models.FileField(default="", upload_to='promotions/', validators=[valid_image_extension])

    class Meta:
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'

    @classmethod
    def get_promotions_actives(cls):

        promotions_with_profiles = []
        now = datetime.datetime.now()
        promotions = cls.objects.filter(active=True, date_init__lt = now , date_finish__gt = now )
        for promotion in promotions:
            len_profiles = []
            promotion_platforms = PromotionPlatform.objects.filter(promotion=promotion)
            for promotion_platform in promotion_platforms:
                profiles = Profile.search_profiles_no_saled(promotion_platform.platform_id)

                len_profiles.append(len(profiles))
            if not 0 in len_profiles:
                promotions_with_profiles.append(promotion)
        return promotions_with_profiles



class PromotionPlatform(models.Model):

    promotion = models.ForeignKey(Promotion, verbose_name="Promoción", on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, verbose_name="Plataforma", on_delete=models.CASCADE)


class PromotionSale(models.Model):

    date = models.DateTimeField(verbose_name="Fecha", auto_now_add=True)
    promotion = models.ForeignKey(Promotion, verbose_name="Promoción", on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, verbose_name="Plataforma", on_delete=models.CASCADE)

class Profile(models.Model):

    count = models.ForeignKey(Count, verbose_name="Plataforma", on_delete=models.CASCADE)
    profile = models.CharField(max_length=100, verbose_name="Perfil")
    pin = models.CharField(max_length=5, verbose_name="Pin", default="0")
    saled = models.BooleanField(default=0, verbose_name="Vendida?:")

    #mixin
    #@receiver(post_save, sender=Count, dispatch_uid="creaction_of_profiles_by_count")
    def create_profiles(sender, instance, **kwargs):

        num_profiles = instance.platform.num_profiles
        for profile in range(num_profiles):
            Profile.objects.create(count=instance, profile=profile )
        return None

    def get_profiles_avaliable(sales, platform_id):

        from collections import Counter
        platform = Platform.objects.filter(id=platform_id).first()
        sales_profiles = list(sales.values_list('profile__profile', flat=True))
        repeats = []
        availables = []
        for x in range(1, int(platform.num_profiles) + 1):
            freq = Counter(sales_profiles).get(str(x))
            if freq:
                if freq > 1:
                    repeats.append(x)
            else:
                availables.append(x)
        have_avaliable = True if len(availables) > 0 else False

        return have_avaliable, availables, repeats


    @classmethod
    def search_profiles_no_saled(cls, platform_id):

        profiles = cls.objects.filter(saled=0, count__platform_id=platform_id)
        return profiles

    @classmethod
    def search_profiles_no_saled_by_plan(cls, plan_id):

        profiles = cls.objects.filter(saled=0, count__plan_id=plan_id)
        count = 0
        if len(profiles) > 0:
            count =  profiles[0].count.plan.num_profiles
        return  profiles, count,

    @classmethod
    def change_password_to_perfile_message(cls, count, profile, now):

        if profile:
            profiles = [ profile ]
        else:
            profiles = cls.objects.filter(count=count)
        for profile in profiles:
            sale = Sale.search_customer_by_profile(profile, now)
            if sale:
                if not profile.count.plan.have_link:
                    message = f"Hola " + sale.bill.customer.name + ", Por motivos de seguridad la contraseña de tu cuenta ha sido cambiada: \n" \
                        f"Plataforma :" + count.platform.name + "\n" \
                        f"Correo : " + count.email + "\n" \
                        f"Nueva Contraseña " + count.password + "\n" \
                        f"Pin " + profile.pin + "\n" \
                        "Lamentamos el inconveniente, sigue disfrutando de tu servicio. \n" \
                        "Atte: El gamer Mx"

                else:
                    message = f"Hola " + sale.bill.customer.name + ", Por motivos de seguridad la contraseña de tu cuenta ha sido cambiada: \n" \
                              f"Plataforma :" + count.platform.name + "\n" \
                              f"link : " + count.link + "\n" \
                              f"Perfil " + profile.profile + "\n" \
                              "Lamentamos el inconveniente, sigue disfrutando de tu servicio. \n" \
                              "Atte: El gamer Mx"
                print(message)
                customer_number = str(sale.bill.customer.phone)
                # send_message(customer_number, message)
class Price(models.Model):

    platform = models.ForeignKey(Platform, verbose_name="Plataforma", on_delete=models.CASCADE)
    num_profiles = models.PositiveIntegerField( verbose_name="Número de perfiles")
    price = models.FloatField(default=0, verbose_name="Precio")

    class Meta:
        verbose_name = 'Precio'
        verbose_name_plural = 'Precios'


class Bill(models.Model):

    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, verbose_name="Cliente", on_delete=models.CASCADE)
    saler = models.ForeignKey(User, verbose_name="Vendedor", on_delete=models.CASCADE)
    total = models.FloatField(default=0, verbose_name="Precio")

    @classmethod
    def GetInterdatesBills(cls, user, initial_date, final_date):

        initial_date = datetime.datetime.strptime(initial_date, '%Y-%m-%d')
        final_date = datetime.datetime.strptime(final_date, '%Y-%m-%d')
        initial_date = initial_date + datetime.timedelta(hours=5)
        final_date = final_date + datetime.timedelta(hours=29)
        bills = cls.objects.filter(saler=user, date__range=[initial_date, final_date]).order_by('-date')
        return bills

class Sale(models.Model):

    date = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="Perfil")
    months = models.PositiveIntegerField(default=1)
    date_limit = models.DateTimeField(verbose_name="Fecha de vencimiento", blank=True, null=True, auto_now_add=False)
    bill = models.ForeignKey(Bill, verbose_name="Factura", on_delete=models.CASCADE)
    renovated = models.BooleanField(default=0, verbose_name="Renovada:")
    cutted = models.BooleanField(default=0, verbose_name="Cortado:")

    @classmethod
    def search_customer_by_profile(cls, profile, now):
        sale = cls.objects.filter(profile=profile, date_limit__gte=now).last()
        return sale

    @classmethod
    def GetInterdatesSales(cls, user, initial_date, final_date):

        initial_date = datetime.datetime.strptime(initial_date, '%Y-%m-%d')
        final_date = datetime.datetime.strptime(final_date, '%Y-%m-%d')
        initial_date = initial_date + datetime.timedelta(hours=5)
        final_date = final_date + datetime.timedelta(hours=29)
        sales = cls.objects.filter(bill__saler=user, date__range=[initial_date, final_date]).order_by('-date')
        return sales

    def set_renovation(self, saler, months,  CalculateDateLimit):

        date_limit = CalculateDateLimit(self.date_limit, months)
        bill = Bill.objects.create(customer=self.bill.customer, saler=saler, total=total)
        self.objects.create(
                            months=months,
                            date_limit=date_limit,
                            bill=saler)

    def cancel_sale(self):
        self.profile.saled = 0
        self.profile.save()
        self.delete()

    def change_count_password(self, new_password):

        self.count.password  = new_password
        self.count.save()



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

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View  # PARA VISTAS GENERICAS
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .decorators import usertype_in_view
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .forms import SaleForm, GetInterDatesForm, CountForm, CreatePromotionForm, PlatformForm, CreatePlatformForm, RenovationForm
from .models import Profile, Count, Platform, Promotion, PromotionPlatform, Price, Bill, Sale, PromotionSale
from user.models import Customer
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.conf import settings
from django.contrib.auth.models import User
from count.decorators import usertype_in_view, check_user_type
from .libraries import getDifference
import datetime, pytz
from django.contrib import messages
from count.libraries import CalculateDateLimit
from user.whatsapp_api import message_sale, message_renew
from django.views.decorators.csrf import csrf_exempt

utc = pytz.UTC
now = datetime.datetime.now()
now = now.replace(tzinfo=utc)

@method_decorator(login_required, name='dispatch')
class DashboardView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard.html')

@method_decorator(usertype_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CreateCount(View):

    template_name = "count/create.html"
    form_class = CountForm

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, *args, **kwargs):

        new_count = Count.objects.create(platform_id = request.POST['platform'],
                                         email = request.POST['email'],
                                         password = request.POST['password'],
                                         date_limit = request.POST['date_limit']
                                         )
        for item in request.POST:
            if item.isnumeric():
                Profile.objects.create(count=new_count, profile = item, pin=request.POST[item], saled=0)
        return redirect("count-list")


@method_decorator(usertype_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class AddPlatformView(CreateView):
    form_class = CreatePlatformForm
    template_name = "platform/add.html"

    def form_valid(self, form):

        form = CreatePlatformForm(self.request.POST, self.request.FILES)
        platform = form.save()
        for item in self.request.POST:
            if item.isnumeric():
               Price.objects.create(platform=platform, num_profiles= item, price= self.request.POST[item])

        return redirect('platform-list')


@method_decorator(usertype_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UpdatePlatformView(UpdateView):

    model = Platform
    fields = ["name", "logo", "num_profiles", "active"]
    template_name = "platform/update.html"
    success_url = "/count/platform/list"


@method_decorator(usertype_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SetPricesOfQuantityProfilesView(View):


    template_name = "profiles/set_prices.html"

    def get(self, request, *args, **kwargs):

        num_profiles = list(range(1, int(kwargs['quantity'])+1))
        return render(request, self.template_name, {'num_profiles': num_profiles})




@method_decorator(login_required, name='dispatch')
class PlatformListView(ListView):

    model = Platform
    template_name = "platform/list.html"

    def get_queryset(self, *args, **kwargs):
        platforms = self.model.objects.filter(active=True)
        return platforms


@method_decorator(usertype_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CreatePinsProfiles(View):

     template_name = "count/num_profiles.html"
     model_class = Platform
     def get(self, request, *args, **kwargs):

         profiles = []
         num_profiles = self.model_class.get_num_of_profiles(kwargs['platform'])
         for num in range(num_profiles):
            profiles.append(num)
         return render(request, self.template_name, {'profiles': profiles})



@method_decorator(login_required, name='dispatch')
@method_decorator(usertype_in_view, name='dispatch')
class CountsListView(ListView):

    model = Bill
    template_name = "count/list.html"

    def get_queryset(self,  *args, **kwargs):

        bills = self.model.objects.all().order_by('date')
        bills_list = []
        for bill in bills:
            sales = Sale.objects.filter(bill=bill)
            bill.sale = sales.first()
            bill.len= len(sales)
            if len(sales) == 0:
                continue
            rest_days =  getDifference(now, sales.first().date_limit, 'days')
            if rest_days < 0:
                bill.rest_days = "Vencida"
            else:
                bill.rest_days = str(rest_days) + " dia(s)"
            bills_list.append(bill)
        return bills_list


@method_decorator(login_required, name='dispatch')
@method_decorator(usertype_in_view, name='dispatch')
class ProfileExpiredView(ListView):

    model = Sale
    template_name = "count/list-to-expire.html"

    def get_queryset(self,  *args, **kwargs):

        date_init = datetime.datetime.now() - datetime.timedelta(days=2)
        date_finish = datetime.datetime.now() + datetime.timedelta(days=3)
        count_to_expires = self.model.objects.filter(profile__saled=True, date_limit__range=[date_init , date_finish ]).order_by('date')
        for sale in count_to_expires:
            rest_days = getDifference(now, sale.date_limit, 'days')
            if rest_days < 0:
                sale.rest_days = "Vencida"
            else:
                sale.rest_days = str(rest_days) + " dia(s)"
        return count_to_expires


@method_decorator(login_required, name='dispatch')
@method_decorator(usertype_in_view, name='dispatch')
class ReactivateProfileView(View):

    def get(self, request, *args, **kwargs):

        try:
            print(kwargs['id'])
            profile = Profile.objects.filter(id = kwargs['id']).first()
            profile.saled=False
            profile.save()
            return HttpResponse("El perfil se activo para venta")
        except:
            return HttpResponse('Hubo un error, contacte al administrador del sistema')



@method_decorator(login_required, name='dispatch')
class AddSaleView(View):

    form_class = SaleForm
    template_name = "sale/add.html"

    def get(self, request, *args, **kwargs):

        customer = Customer.objects.filter(id= kwargs['id']).first()
        if customer:
            promotions = Promotion.get_promotions_actives()
            return render(request, self.template_name, { 'form': self.form_class,  'customer':customer, 'promotions':promotions })
        else:
            return redirect('index')


    def post(self, request, *args, **kwargs):

        profiles = []
        form = self.form_class (request.POST)
        customer = Customer.objects.filter(id= kwargs['id']).first()
        if customer and form.is_valid():
            num_profiles = list(request.POST.values()).count("on")
            total = Price.objects.filter(platform_id = request.POST['platform'], num_profiles= num_profiles).first()
            bill = Bill.objects.create(customer=customer, saler= request.user, total=total.price)
            for item in request.POST:
                if item.isnumeric():
                    if request.POST[item] == 'on':
                        date_limit = CalculateDateLimit(now, int(request.POST['months']))
                        profile = Profile.objects.filter(id = item).first()
                        profile.pin = request.POST['pin_'+item]
                        profile.profile = request.POST['profile_'+item]
                        profile.save()
                        profiles.append(profile)
                        request.user.sale_profile( profile, int(request.POST['months']), date_limit, bill)
                        message_sale(profile, customer, date_limit)
            return render(request, 'sale/sale_post.html', { 'profiles':profiles })

        return render(request, self.template_name, {'form': self.form_class, 'customer': customer})

@method_decorator(login_required, name='dispatch')
class GetProfilesAvailableView(ListView):

    model = Profile
    template_name = "profiles/list_avaliables.html"

    def get_queryset(self,  *args, **kwargs):

        profiles = self.model.search_profiles_no_saled(self.kwargs['platform'])
        return profiles





@method_decorator(login_required, name='dispatch')
class BillListView(ListView):

    model = Bill
    template_name = "bill/list.html"

    def get_queryset(self,  *args, **kwargs):

        bills = self.model.objects.filter(saler=self.request.user).order_by('-date')
        return bills


@method_decorator(login_required, name='dispatch')
class SalesListView(ListView):
    model = Sale
    template_name = "sale/list.html"

    def get_queryset(self, *args, **kwargs):

        sales = self.model.objects.filter(bill=self.kwargs['id'], bill__saler=self.request.user)
        for sale in sales:
            rest_days = getDifference( now, sale.date_limit, 'days')
            if rest_days < 0:
                sale.rest_days = "Vencida"
            else:
                sale.rest_days = rest_days
        return sales

    def post(self, request, *args, **kwargs):

        num_profiles = list(request.POST.values()).count("on")
        for item in request.POST:
            if item.isnumeric():
                profile = Profile.objects.filter(id=item).first()
                sale = Sale.objects.filter(profile=item).last()
                continue
        total = Price.objects.filter(platform=profile.count.platform, num_profiles=num_profiles).first()
        bill = Bill.objects.create(customer=sale.bill.customer, saler=request.user, total=total.price)
        for item in request.POST:
            if item.isnumeric():
                if request.POST[item] == 'on':
                    profile = Profile.objects.filter(id=item).first()
                    date_limit = CalculateDateLimit(now, int(request.POST['months']))
                    profile_saled = request.user.sale_profile(profile, int(request.POST['months']), date_limit, bill)
                    message_renew(profile, sale.bill.customer, date_limit)

        return redirect('bill-list')


@method_decorator(login_required, name='dispatch')
class InterdatesSalesView(ListView):

    model = Bill
    template_name = "sale/list-no-layout.html"

    def get_queryset(self, *args, **kwargs):

        if 'user' in kwargs:
            user = User.objects.filter(username = kwargs['user'])
        else:
            user = self.request.user

        bills = self.model.GetInterdatesBills(user, self.kwargs['initial_date'],
                                                  self.kwargs['final_date'] )
        return bills


@method_decorator(usertype_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CreatePromotionView(View):

    model = Promotion
    template_name = "promotion/create.html"

    def get(self, request, *args, **kwargs):
        counts = []
        platforms =  Platform.objects.filter(active=True)
        for platform in platforms:
            list = []
            for profile in range(platform.num_profiles):
                list.append(profile)
                counts.append(( platform.name+'_'+ str(profile), platform.name))
            platform.list = list
        form = CreatePromotionForm()
        form_platform = PlatformForm()
        form_platform.fields['platforms'].choices = counts
        return render(request, self.template_name, { 'form':form, 'platforms': platforms, 'form_platform':form_platform })

    def post(self, request, *args, **kwargs):

        form = CreatePromotionForm(request.POST, request.FILES)
        if form.is_valid():
            promotion = form.save(commit=False)
            promotion.creater = request.user
            promotion.date_init = request.POST['date_init'] + " 00:00:01.850566"
            promotion.date_finish = request.POST['date_finish'] + " 23:59:59.850566"
            promotion.save()
            for platform_name_profle in request.POST.getlist('platforms'):
                platform_name_list = platform_name_profle.split("_")
                platform = Platform.objects.filter(name=platform_name_list[0]).first()
                PromotionPlatform.objects.create(promotion=promotion, platform= platform)
            return redirect('index')
        return render(request, self.template_name, {'form': form})

@method_decorator(login_required, name='dispatch')
class ListPromotionView(ListView):

    model = Promotion
    template_name = "promotion/list.html"

    def get_queryset(self, *args, **kwargs):
        promotions = self.model.objects.filter(active=True).order_by('-date_finish')
        return promotions


class SalePromotionView(View):


    model = Promotion
    template_name = "promotion/sale.html"

    def post(self, request, *args, **kwargs):

        profiles = []
        customer = Customer.objects.filter(id=kwargs['user_id']).first()
        promotion = Promotion.objects.filter(id=kwargs['promotion_id']).first()
        promotion_platforms = PromotionPlatform.objects.filter(promotion_id=kwargs['promotion_id'])
        bill = Bill.objects.create(customer=customer, saler=request.user, total=promotion.price)
        for promotion_platform in promotion_platforms:
            profile = Profile.search_profiles_no_saled(promotion_platform.platform_id)[0]
            date_limit = CalculateDateLimit(now, int(request.POST['months_promo']))
            profiles.append(profile)
            request.user.sale_profile(profile, int(request.POST['months_promo']), date_limit, bill)
            message_sale(profile, customer, date_limit)
        PromotionSale.objects.create(promotion=promotion, customer=customer )

        return render(request, 'sale/sale_post.html', {'profiles': profiles})


class CronWhatsappView(ListView):
    pass


@method_decorator(login_required, name='dispatch')
class InterDatesView(View):

    def get(self, request, *args, **kwargs):

        ctx = {}
        form = GetInterDatesForm()
        ctx['form'] = form
        ctx['titles'] = settings.TITLES_INTER_DATES[kwargs['model']]
        if 'user' in kwargs:
            ctx['username'] = kwargs['user']

        return render(request, 'inter-dates.html', ctx)
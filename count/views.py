from django.shortcuts import render, redirect, get_object_or_404
from django.views import View  # PARA VISTAS GENERICAS
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .decorators import usertype_in_view
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .forms import SaleForm, GetInterDatesForm, CountForm, CreatePromotionForm, PlatformForm, CreatePlatformForm, RenovationForm, ChangePaswordForm, ChangeDateLimitForm, ChangeCountDataForm
from .models import Profile, Count, Platform, Promotion, PromotionPlatform, Price, Bill, Sale, PromotionSale
from user.models import Customer, Action
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.conf import settings
from django.contrib.auth.models import User
from count.decorators import usertype_in_view, check_user_type
from .libraries import getDifference
import datetime, pytz, json
from django.contrib import messages
from count.libraries import CalculateDateLimit
from user.whatsapp_api import message_sale, message_renew
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.urls import reverse_lazy




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

    model = Count
    template_name = "count/list.html"

    def get_queryset(self,  *args, **kwargs):

        counts = self.model.objects.all()
        return None


@method_decorator(login_required, name='dispatch')
@method_decorator(usertype_in_view, name='dispatch')
class CountListJson(BaseDatatableView):

    columns = ['Plataforma', 'Correo', 'Perfiles', 'Disponibles', 'Contraseña', 'Vence']
    order_columns = ['date']
    model = Count
    #max_display_length = 500

    def get_initial_queryset(self):

        counts = self.model.objects.all().order_by('-date')

        return counts

    def render_column(self, row, column):
        return super(OrderListJson, self).render_column(row, column)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            q = Q(email__icontains=search) | Q(platform__name__icontains=search)
            qs = qs.filter(q)

        return qs

    def prepare_results(self, qs):

        json_data = []

        for item in qs:

            profiles = Profile.objects.filter(count=item)
            len_profiles = len(profiles)
            profiles_available = len(profiles.filter(saled=False))
            rest_days = getDifference(now, item.date_limit, 'days')
            if rest_days < 0:
                rest_days = "Vencida"
            else:
                rest_days = str(rest_days) + " dia(s)"

            link_change= f'<button type="button" id_count="{ item.id }" class="btn btn-warning change-password">Cambiar</button>'
            link_detele= f'<button type="button" id_count="{ item.id }" class="btn btn-danger delete-count">Eliminar</button>' #link2 = f'<a href="/user/update-customer/{item.id}"><button type="button" class="btn btn-info  btn-icon-text"><i class="mdi mdi-information"></i>Editar</button></a>'
            json_data.append([
                item.platform.name,
                item.email,
                len_profiles,
                profiles_available,
                item.password,
                rest_days,
                link_change,
                link_detele
            ])
        return json_data

@method_decorator(login_required, name='dispatch')
@method_decorator(usertype_in_view, name='dispatch')
class CountNextExpiredView(ListView):

    model = Count
    template_name = "count/list-to-expire.html"

    def get_queryset(self,  *args, **kwargs):

        #date_init = datetime.datetime.now() - datetime.timedelta(days=2)

        date_finish = datetime.datetime.now() + datetime.timedelta(days=3)
        count_to_expires = self.model.objects.filter(date_limit__range=[datetime.datetime.now()  , date_finish ]).order_by('date_limit')
        for count in count_to_expires:
            profiles = Profile.objects.filter(count=count)
            count.profiles_available = len(profiles.filter(saled=False))
            rest_days = getDifference(now, count.date_limit, 'days')
            if rest_days < 0:
                cccccrest_days = "Vencida"
            else:
                count.rest_days = str(rest_days) + " dia(s)"
        return count_to_expires


@method_decorator(login_required, name='dispatch')
@method_decorator(usertype_in_view, name='dispatch')
class CountExpiredView(ListView):

    model = Count
    template_name = "count/list-expired.html"

    def get_queryset(self,  *args, **kwargs):

        count_expired = self.model.objects.filter(date_limit__lt=datetime.datetime.now()).order_by('date')
        for count in count_expired:
            profiles = Profile.objects.filter(count=count)
            count.profiles_available = len(profiles.filter(saled=False))
        return count_expired


@method_decorator(login_required, name='dispatch')
@method_decorator(usertype_in_view, name='dispatch')
class ChangeDateLimitView(View):

    model = Count
    form_class = ChangeDateLimitForm
    template_name = 'count/change_date_limit.html'
    permission_required = 'count.change_count'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name,  {'form': self.form_class, 'id':kwargs['id'] })
    def post(self, request, *args, **kwargs):

        date_now = datetime.datetime.now()
        date_now = date_now +  datetime.timedelta(days=1)
        date_limit = datetime.datetime.strptime(request.POST['date_limit'], '%Y-%m-%d')
        if date_limit > date_now:
            count = self.model.objects.filter(id=kwargs['id']).first()
            count.date_limit = date_limit
            count.save()
            return HttpResponse("Fecha de finalización cambiada con éxito")
        else:
            return HttpResponse("La fecha aregistrada tiene que ser mayor quela fecha actual")

@method_decorator(login_required, name='dispatch')
@method_decorator(usertype_in_view, name='dispatch')
class EditCountDataView(View):

    model = Profile
    form_class = ChangeCountDataForm
    template_name = 'count/change_password.html'
    permission_required = 'count.change_count'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name,  {'form': self.form_class, 'id':kwargs['id'] })
    def post(self, request, *args, **kwargs):

        profile = self.model.objects.filter(id=kwargs['id']).first()
        count = Count.objects.filter(id=profile.count.id).first()
        count.password = request.POST['password']
        profile.pin = request.POST['pin']
        profile.save()
        count.save()
        return HttpResponse("Datos Actualizados")






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
        profiles_json = {}
        form = self.form_class (request.POST)
        customer = Customer.objects.filter(id= kwargs['id']).first()
        if customer and form.is_valid():
            num_profiles = list(request.POST.values()).count("on")
            total = Price.objects.filter(platform_id = request.POST['platform'], num_profiles= num_profiles).first()
            bill = Bill.objects.create(customer=customer, saler= request.user, total=total.price)
            i=0
            for item in request.POST:
                if item.isnumeric():
                    if request.POST[item] == 'on':
                        date_limit = CalculateDateLimit(now, int(request.POST['months']))
                        profile = Profile.objects.filter(id = item).first()
                        profile.pin = request.POST['pin_'+item]
                        profile.profile = request.POST['profile_'+item]
                        profile_json = {"platform": profile.count.platform.name,
                                        "email":profile.count.email,
                                        "password":profile.count.password,
                                        "phone":str(customer.phone),
                                        "date_limit":str(date_limit.strftime('%d/%m/%Y')),
                                        "profile":profile.profile,
                                        "pin":profile.pin}
                        profiles_json[i] = profile_json
                        profile.save()
                        profiles.append(profile)
                        i+=1
                        request.user.sale_profile( profile, int(request.POST['months']), date_limit, bill)

            return render(request, 'sale/sale_post.html', { 'profiles':profiles,  'profiles_json': json.dumps(profiles_json) })

        return render(request, self.template_name, {'form': self.form_class })


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SendMessageWhatsapp(View):
    def post(self, request, *args, **kwargs):

        json_data = json.loads(request.body)
        try:
            data = json.loads(json_data)
            for item in data:
                message_sale(data[item])
        except:
            message_sale(json_data)
        return HttpResponse("Mensaje enviado")




@method_decorator(login_required, name='dispatch')
class GetProfilesAvailableView(ListView):

    model = Profile
    template_name = "profiles/list_avaliables.html"

    def get_queryset(self,  *args, **kwargs):

        profiles = self.model.search_profiles_no_saled(self.kwargs['platform'])
        return profiles

@method_decorator(login_required, name='dispatch')
class CancelSaleView(View):

    model = Sale
    def get(self, request, *args, **kwargs):

        sale = self.model.objects.filter(id=self.kwargs['id']).first()
        Action.action_register(request.user, "Cancelación de la venta id = "+ str(sale.id) + " del dia " + str(sale.date) + " factura :" + str(sale.bill.id) + " cuenta :" + str(sale.profile.count.email))
        sale.cancel_sale()


        return HttpResponse("Venta cancelada")


@method_decorator(login_required, name='dispatch')
class ChangeCountPasswordView(View):

    model = Count
    template_name = "count/change_password.html"
    form_class = ChangePaswordForm
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,  {'form': self.form_class, 'id':kwargs['id'] })

    def post(self, request, *args, **kwargs):

        count = self.model.objects.filter(id=self.kwargs['id']).first()
        Action.action_register(request.user, "Cambio password de cuenta id = "+ str(count.id) + " del dia " + str(count.date) )
        count.password = request.POST['password']
        count.save()
        return HttpResponse("Contraseña editada conrrectamente")
#
#     def get(self, request, *args, **kwargs):
#
#         sale = self.model.objects.filter(id=self.kwargs['id']).first()
#         Action.action_register(request.user, "Cancelación de la venta id = "+ str(sale.id) + " del dia " + str(sale.date) + " factura :" + str(sale.bill.id) + " cuenta :" + str(sale.profile.count.email))
#         sale.cancel_sale()
#
#
#         return HttpResponse("Venta cancelada")




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

        total = 0
        counts = {}
        bill = Bill.objects.create(customer_id=kwargs['id'], saler=request.user, total=0)
        for item in request.POST:
            if item.isnumeric():
                if request.POST[item] == 'on':
                    profile = Profile.objects.filter(id=item).first()
                    if not profile.count.id in counts:
                        counts[profile.count.id] = { "amount": 1 }
                    else:
                        counts[profile.count.id]['amount'] = counts[profile.count.id]['amount'] + 1
                    counts[profile.count.id]["platform"] = profile.count.platform.id
                sale = Sale.objects.filter(profile=profile).last()
                date_limit = CalculateDateLimit(sale.date_limit, int(request.POST['months']))
                request.user.sale_profile(profile, int(request.POST['months']), date_limit, bill)
                message_renew(profile, sale.bill.customer, date_limit)

        for key in counts:
            subtotal = Price.objects.filter(platform_id=counts[key]['platform'], num_profiles=counts[key]['amount'] ).first()
            total = total + subtotal.price
        bill.total = total
        bill.save()
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



@method_decorator(login_required, name='dispatch')
class CountDeleteView(View):

    model = Count

    def get(self, request, *args, **kwargs):
        try:
            count = Count.objects.filter(id=kwargs['pk']).first()
            count.delete()
            return HttpResponse("La cuenta has sido eliminada permanentemente.")

        except:
            return HttpResponse("Hubo un error.")


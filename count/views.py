from django.shortcuts import render, redirect, get_object_or_404
from django.views import View  # PARA VISTAS GENERICAS
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .decorators import permissions_in_view, my_permissions
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .forms import *
from .models import Profile, Count, Platform, Promotion, PromotionPlatform, Price, Bill, Sale, PromotionSale
from user.models import Customer, Action
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.conf import settings
from django.contrib.auth.models import User
from .libraries import getDifference
import datetime, pytz, json
from django.contrib import messages
from count.libraries import CalculateDateLimit
from user.whatsapp_api import message_sale, message_plan_sale, message_renew, message_expired
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q, Count as Count_
from django.urls import reverse_lazy
from datetime import timezone
from django.http import Http404

utc = pytz.UTC
now = datetime.datetime.now()
now = now.replace(tzinfo=utc)

@method_decorator(login_required, name='dispatch')
class DashboardView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard.html')



@method_decorator(permissions_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CreatePlan(View):

    template_name = "plan/create.html"
    form_class = PlanForm

    def dispatch(self, request, *args, **kwargs):

        platform = Platform.objects.filter(name=kwargs.get('platform')).first()
        if platform :
            self.platform = platform
        else:
            raise Http404("La plataforma no existe")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, platform, *args, **kwargs):


        if self.platform:
            form = self.form_class(self.platform)
            return render(request, self.template_name, {'form': form, 'platform': self.platform})
        else:
            return redirect("platform-list")

    def post(self, request, *args, **kwargs):

        plan = Plan.objects.create(platform = self.platform,
                                         name = request.POST['name'],
                                         num_profiles = request.POST['num_profiles'],
                                         have_link = request.POST['have_link'],
                                         active = request.POST['active'],
                                         description = request.POST['description']
                                         )
        return redirect('update-platform', self.platform.id)

@method_decorator(permissions_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UpdatePlanView(UpdateView):

    model = Plan
    fields = ["name", "num_profiles", "active", "have_link",  "description"]
    template_name = "plan/update.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        platform = self.get_object()
        context['platform_name'] = platform.name
        return context

    def get_success_url(self):

        plan = self.get_object()
        success_url = "/count/plan/list/list/"+plan.platform.name
        return success_url

@method_decorator(login_required, name='dispatch')
class PlanListView(ListView):

    model = Plan

    def get_queryset(self):

        plans = self.model.objects.filter(platform__name=self.kwargs['platform'], active=True)
        return plans

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['platform_name'] = self.kwargs['platform']
        return context

    def get_template_names(self):

        template_name = self.kwargs.get('template_name')
        if template_name:
            return [f'plan/{template_name}.html']
        else:
            raise Http404("Template no encontrado")







@method_decorator(permissions_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CreateCount(View):

    template_name = "count/create.html"
    form_class = CountForm

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, *args, **kwargs):

        plan_id = request.POST['plan'] if 'plan' in request.POST else None
        new_count = Count.objects.create(platform_id = request.POST['platform'],
                                         plan_id = plan_id,
                                         email = request.POST['email'],
                                         country_id=request.POST['country'],
                                         link=request.POST['link'] if 'link' in request.POST else "",
                                         password = request.POST['password'],
                                         email_password=request.POST['email_password'],
                                         date_limit = request.POST['date_limit']
                                         )

        for item in request.POST:
            if item.isnumeric():
                Profile.objects.create(count=new_count, profile = item, pin=request.POST[item], saled=0)
        return redirect("count-list")



@method_decorator(permissions_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UpdateCount(UpdateView):

    template_name = "count/update.html"
    form_class = CountUpdateForm

    def get(self, request, id, *args, **kwargs):

        count= Count.objects.filter(id=id).first()
        profiles= Profile.objects.filter(count=count)
        form = self.form_class(instance=count)
        return render(request, self.template_name, {'form': form, 'profiles':profiles, 'platform': count.plan.platform if count.plan else count.platform})

    def post(self, request, id, *args, **kwargs):


        count = Count.objects.filter(id=id).first()
        country = Country.objects.filter(id=request.POST['country']).first()
        count.email = request.POST['email']
        count.country = country
        count.date_limit = request.POST['date_limit']
        count.save()
        for item in request.POST:
            if item.isnumeric():
                profile = Profile.objects.filter(count=count, profile = item).first()
                profile.pin=request.POST[item]
                profile.save()
        return redirect("count-list")


@method_decorator(login_required, name='dispatch')
class SelectPlan(View):

    template_name = "count/select-plan-by-platform.html"
    form_class = CountPlanForm

    def get(self, request, platform_id,  *args, **kwargs):

        form =self.form_class(platform_id)

        return render(request, self.template_name, {'form': form })


@method_decorator(permissions_in_view, name='dispatch')
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


@method_decorator(permissions_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UpdatePlatformView(UpdateView):

    model = Platform
    fields = ["name", "logo", "num_profiles", "active"]
    template_name = "platform/update.html"
    success_url = "/count/platform/list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        platform = self.get_object()
        context['platform_name'] = platform.name
        return context



@method_decorator(permissions_in_view, name='dispatch')
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



@method_decorator(permissions_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CreatePinsProfiles(View):

     template_name = "count/num_profiles.html"
     model_class_platform = Platform
     model_class_plan = Plan
     def get(self, request, *args, **kwargs):

        profiles = []
        have_link = False
        if kwargs['type'] == "platform":
           model = self.model_class_platform
           plans = Plan.objects.filter(platform_id=kwargs['id'])
           if plans:
               return render(request, self.template_name, {'profiles': None})
        elif kwargs['type'] == "plan":
            plan = Plan.objects.filter(id=kwargs['id']).first()
            have_link = plan.have_link
            model = self.model_class_plan
        num_profiles = model.get_num_of_profiles(kwargs['id'])
        for num in range(num_profiles):
            profiles.append(num)

        return render(request, self.template_name, {'profiles': profiles, 'have_link':have_link})


@method_decorator(login_required, name='dispatch')
class CountsListView(ListView):

    model = Count
    template_name = "count/list.html"

    def get_queryset(self,  *args, **kwargs):

        counts = self.model.objects.all()
        return None


@method_decorator(login_required, name='dispatch')
class CountListAjax(BaseDatatableView):

    columns = ['Plataforma', 'Plan', 'Correo', 'Perfiles', 'Disponibles', 'Contraseña de cuenta', 'Contraseña de correo', 'pais',  'Vence', 'link']
    order_columns = ['date','platform.name', 'email']
    model = Count
    #max_display_length = 500

    def get_initial_queryset(self):

        counts = self.model.objects.all()
        return counts

    def render_column(self, row, column):
        return super(CountListJson, self).render_column(row, column)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            q = Q(email__icontains=search) | Q(platform__name__icontains=search)
            qs = qs.filter(q)

        return qs

    def prepare_results(self, qs):

        json_data = []
        rest_days = "indeterminado"
        permissions = my_permissions(self.request.user)
        for item in qs:
            now = datetime.datetime.now(timezone.utc)
            profiles = Profile.objects.filter(count=item)
            len_profiles = len(profiles)
            profiles_available = len(profiles.filter(saled=False))
            if item.date_limit:
                rest_days = getDifference(now, item.date_limit ,  'days')
                if rest_days < 0:
                    rest_days = "Vencida"
                else:
                    rest_days = str(rest_days) + " dia(s)"
            if 'change_count' in permissions:
                link_change_password = f'<button type="button" id_count="{ item.id }" class="btn btn-warning change-password">Cambiar password de cuenta</button>'
                link_change_password_email = f'<button type="button" id_count="{ item.id }" class="btn btn-info change-password-email">Cambiar password de correo</button>'
                link_change_date = f'<button type="button" id_count="{item.id}" class="btn btn-primary btn-icon-text change-date-limit">Cambiar fecha</button>'
                link_update = f'<a href="/count/update/{item.id}" type="button"  class="btn btn-success btn-icon-text"><i class="mdi mdi-grease-pencil"></i>Editar</a>'
            else:
                link_change_password = ''
                link_change_password_email = ''
                link_change_date = ''
            if 'delete_count' in permissions:
                link_delete= f'<button type="button" id_count="{ item.id }" class="btn btn-danger delete-count">Eliminar</button>'
            else:
                link_delete = ''

            if item.plan:
                json_data.append([
                    item.platform.name,
                    item.plan.name,
                    item.email,
                    len_profiles,
                    profiles_available,
                    item.password,
                    item.email_password,
                    item.country.country,
                    rest_days,
                    item.link,
                    link_change_password,
                    link_change_password_email,
                    link_change_date,
                    link_update,
                    link_delete
                ])
            else:
                json_data.append([
                    item.platform.name,
                    "",
                    item.email,
                    len_profiles,
                    profiles_available,
                    item.password,
                    item.email_password,
                    item.country.country,
                    rest_days,
                    item.link,
                    link_change_password,
                    link_change_password_email,
                    link_change_date,
                    link_update,
                    link_delete
                ])
        return json_data

@method_decorator(login_required, name='dispatch')
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
                rest_days = "Vencida"
            else:
                count.rest_days = str(rest_days) + " dia(s)"
        return count_to_expires


@method_decorator(login_required, name='dispatch')
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
@method_decorator(permissions_in_view, name='dispatch')
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
@method_decorator(permissions_in_view, name='dispatch')
class EditCountDataView(View):

    model = Profile
    form_class = ChangeCountDataForm
    template_name = 'count/change_password.html'
    permission_required = 'count.change_count'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name,  {'form': self.form_class, 'id':kwargs['id'], 'type': kwargs['type'] })
    def post(self, request, *args, **kwargs):

        change_password = change_pin = False
        profile = self.model.objects.filter(id=kwargs['id']).first()
        count = Count.objects.filter(id=profile.count.id).first()
        if not request.POST['password'] == "":
            count.password = request.POST['password']
            change_password =True
        if not request.POST['pin'] == "":
            profile.pin = request.POST['pin']
            change_pin =True
        profile.save()
        if change_password:
            Profile.change_password_to_perfile_message(count, None,  now)
        elif change_pin:
            Profile.change_password_to_perfile_message(count, profile, now)
        count.save()

        return HttpResponse("Cuenta Actualizados")


@method_decorator(login_required, name='dispatch')
@method_decorator(permissions_in_view, name='dispatch')
class EditSaleDataView(View):

    model = Sale

    template_name = 'count/change_sale.html'
    permission_required = 'count.change_sale'

    def get(self, request, *args, **kwargs):
        form_class = ChangeSaleDataForm(kwargs['id'])
        return render(request, self.template_name,  {'form': form_class, 'id':kwargs['id'] })

    def post(self, request, *args, **kwargs):

        sale = self.model.objects.filter(id=kwargs['id']).first()
        if not request.POST['date'] == "":
            sale.date = request.POST['date']
        if not request.POST['date_limit'] == "":
            sale.date_limit = request.POST['date_limit']
        sale.save()
        return HttpResponse("Venta Actualizados")



@method_decorator(login_required, name='dispatch')
@method_decorator(permissions_in_view, name='dispatch')
class CutProfileView(View):

    def get(self, request, *args, **kwargs):

        try:
            sales = Sale.objects.filter(id= kwargs['sale_id'], profile_id= kwargs['id'] )
            if sales:
                sales.update(cutted = True)
                profile = Profile.objects.filter(id = kwargs['id']).update(saled=False)
                return HttpResponse("El perfil se activo para venta")
            else:
                return HttpResponse('No existe o hubo un error, contacte al administrador del sistema')
        except:
                return HttpResponse('Hubo un error, contacte al administrador del sistema')



@method_decorator(login_required, name='dispatch')
@method_decorator(permissions_in_view, name='dispatch')
class OwnerProfileView(View):

    def get(self, request, *args, **kwargs):

        try:
            sales = Sale.objects.filter( profile_id= kwargs['id'] ).exclude(id = kwargs['sale_id'])
            for sale in sales:
                sale.cutted = True
                sale.save()
            return HttpResponse("Se cortaron los perfiles adicionales")
        except:
            return HttpResponse('Hubo un error, contacte al administrador del sistema')



@method_decorator(login_required, name='dispatch')
@method_decorator(permissions_in_view, name='dispatch')
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
            date_limit = CalculateDateLimit(now, int(request.POST['months']))
            plan = ""
            num_profiles = list(request.POST.values()).count("on")
            total = Price.objects.filter(platform_id = request.POST['platform'], num_profiles= num_profiles).first()
            bill = Bill.objects.create(customer=customer, saler= request.user, total=total.price)
            i=0
            for item in request.POST:
                template = 'sale/sale_post.html'
                if 'plan' in request.POST:
                    if request.POST['plan'] != "":
                        plan = Plan.objects.filter(id=request.POST['plan']).first().name
                        template = 'sale/sale_plan_post.html'
                if item.isnumeric():
                    if request.POST[item] == 'on':
                        profile = Profile.objects.filter(id = item).first()
                        profile.pin = request.POST['pin_'+item]
                        profile.profile = request.POST['profile_'+item]
                        profile_json = {"platform": profile.count.platform.name,
                                        "plan":plan,
                                        "email":profile.count.email,
                                        "password":profile.count.password,
                                        "phone":str(customer.phone),
                                        "date_limit":str(date_limit.strftime('%d/%m/%Y')),
                                        "profile":profile.profile,
                                        "link":profile.count.link,
                                        "pin":profile.pin}
                        profiles_json[i] = profile_json
                        profile.save()
                        profiles.append(profile)
                        i+=1
                        request.user.sale_profile( profile, int(request.POST['months']), date_limit, bill)
            return render(request, template,
                          {'profiles': profiles, 'profiles_json': json.dumps(profiles_json)})

        return render(request, self.template_name, {'form': self.form_class })


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SendMessageWhatsapp(View):
    def post(self, request, *args, **kwargs):

        json_data = json.loads(request.body)
        try:
            data = json.loads(json_data)
            for item in data:
                if 'plan' in data[item]:
                    message_plan_sale(data)
                    continue
                else:
                    message_sale(data[item])
        except:
            message_sale(json_data)
        return HttpResponse("Mensaje enviado")

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SendPlanMessageWhatsapp(View):
    def post(self, request, *args, **kwargs):

        json_data = json.loads(request.body)
        json_data = json.loads(json_data)
        message_plan_sale(json_data)
        return HttpResponse("Mensaje enviado")


class SendMessageWhatsappExpired(SendMessageWhatsapp):
    def post(self, request, *args, **kwargs):

        json_data = json.loads(request.body)
        message_expired(json_data)
        return HttpResponse(str(json_data["profile_id"]))


@method_decorator(login_required, name='dispatch')
class GetProfilesAvailableView(ListView):

    model = Profile
    template_name = "profiles/list_avaliables.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        if 'platform' in self.kwargs:
            profiles = self.model.search_profiles_no_saled(self.kwargs['platform'])
        if 'plan' in self.kwargs:
            profiles, num_profiles  = self.model.search_profiles_no_saled_by_plan(self.kwargs['plan'])
            context['num_profiles'] = num_profiles
        context['profiles'] = profiles

        return context



@method_decorator(login_required, name='dispatch')
class CancelSaleView(View):

    model = Sale
    def get(self, request, *args, **kwargs):

        sale = self.model.objects.filter(id=self.kwargs['id']).first()
        Action.action_register(request.user, "Cancelación de la venta id = "+ str(sale.id) + " del dia " + str(sale.date) + " factura :" + str(sale.bill.id) + " cuenta :" + str(sale.profile.count.email))
        sale.cancel_sale()


        return HttpResponse("Venta cancelada")



@method_decorator(login_required, name='dispatch')
class SearchSaleView(View):

    model = Sale
    template_name = "count/search.html"
    form_class = SearchCountForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,  {'form': self.form_class })


    def post(self, request, *args, **kwargs):

        sales = self.model.objects.filter(profile__saled=True, cutted=False, renovated=False,  profile__count__email=request.POST['email'].strip(), profile__count__platform=request.POST['platform']).order_by('date_limit')
        have_avaliable, availables, repeats = Profile.get_profiles_avaliable(sales, request.POST['platform'])
        for sale in sales:
            rest_days = getDifference( now, sale.date_limit, 'days')
            if  sale.profile.profile in repeats:
                sale.buttom_owner = True
            sale.rest_days = rest_days
        return render(request, "count/search_list.html", { 'sales':sales, 'email': request.POST['email'], 'have_avaliable':have_avaliable })

@method_decorator(login_required, name='dispatch')
class ChangeProfileSaleView(View):

    model = Sale
    template_name = "count/change_profile_sale.html"

    def get(self, request, *args, **kwargs):

        sale = self.model.objects.filter(id=kwargs['pk']).first()
        sales = self.model.objects.filter(profile__saled=True, cutted=False, profile__count__email=sale.profile.count.email.strip()).order_by('date_limit')
        have_avaliable, availables, repeats = get_profiles_avaliable(sales)
        profiles = Profile.objects.filter(count=sale.profile.count, profile__in=availables )
        return render(request, self.template_name,  {'profiles': profiles, 'id':kwargs['pk'] })

    def post(self, request, *args, **kwargs):

        sale = self.model.objects.filter(id=kwargs['pk']).first()
        if sale:
            sale.profile_id = request.POST['profile']
            sale.save()
            profile = Profile.objects.filter(id = request.POST['profile'] ).first()
            profile.saled=True
            profile.save()
            return redirect('search-sale')




@method_decorator(login_required, name='dispatch')
class ChangeTypePasswordView(View):

    model = Count
    template_name = "count/change_password.html"
    form_class_count = ChangePaswordForm
    form_class_email = ChangePaswordEmailForm
    def get(self, request, *args, **kwargs):

        form_class = self.form_class_count if kwargs['type'] == "count"  else self.form_class_email

        return render(request, self.template_name,  {'form': form_class, 'id':kwargs['id'], 'type': kwargs['type'] })

    def post(self, request, *args, **kwargs):

        count = self.model.objects.filter(id=self.kwargs['id']).first()

        if  kwargs['type'] == "count":
            Action.action_register(request.user, "Cambio password de cuenta id = "+ str(count.id) + " del dia " + str(count.date) )
            count.change_count_password(request.POST['password'])
            Profile.change_password_to_perfile_message(count, None, now)

        elif kwargs['type'] == "email":
            Action.action_register(request.user,
                                   "Cambio password de correo id = " + str(count.id) + " del dia " + str(count.date))
            count.change_email_password(request.POST['email_password'])

        return HttpResponse("Contraseña editada conrrectamente")




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
                    sales = Sale.objects.filter(id=item)
                    last_sale = sales.last()
                    sales.update(renovated=True)
                    profile = Profile.objects.filter(id=last_sale.profile_id).first()
                    if not profile.count.id in counts:
                        counts[last_sale.profile.count.id] = { "amount": 1 }
                    else:
                        counts[last_sale.profile.count.id]['amount'] = counts[profile.count.id]['amount'] + 1
                    counts[last_sale.profile.count.id]["platform"] = profile.count.platform.id
                    date_limit = CalculateDateLimit(last_sale.date_limit, int(request.POST['months']))
                    request.user.sale_profile(last_sale.profile, int(request.POST['months']), date_limit, bill)
                    message_renew(last_sale.profile, last_sale.bill.customer.phone, date_limit)

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


@method_decorator(permissions_in_view, name='dispatch')
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


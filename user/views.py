from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import View #PARA VISTAS GENERICAS
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from .models import Customer, UserTwoFactorAuthData
from count.models import Sale, Bill, Profile, Price
from .forms import CustomerForm, UserForm
from count.decorators import permissions_in_view, my_permissions
from django.contrib.auth.models import User
from .whatsapp_api import send_message
import datetime, pytz
from count.libraries import getDifference
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.urls import reverse_lazy
from count.libraries import CalculateDateLimit
from user.whatsapp_api import message_renew
from .libraries import user_two_factor_auth_data_create
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, views as auth_views
from custom_admin.forms import OTPForm
from django.contrib.auth import login, authenticate
from django.conf import settings


utc = pytz.UTC
now = datetime.datetime.now()
now = now.replace(tzinfo=utc)


def context_app(request):
    permissions = my_permissions(request.user)
    context = {}
    if request.user.is_authenticated:
            context['otp_active'] = settings.OPT_ACTIVE
            context['permissions'] = permissions
    return context


class MyLoginView(auth_views.LoginView):

    tamplate_name = 'user/login.html'
    def get(self, request):

        return render(self.request, self.tamplate_name)
    def post(self, request):

        user = authenticate(request=self.request, username=self.request.POST['username'],
                            password=self.request.POST['password'])
        if user :
            if user.is_active:

                two_factor_auth_data = UserTwoFactorAuthData.objects.filter(user__username=request.POST.get('username')).first()
                self.request.session['username'] = str(user.username)
                if two_factor_auth_data:
                    return redirect('confirm-2fa')
                else:
                    return redirect('setup-2fa')

        return render(self.request, self.tamplate_name)



class SetupTwoFactorAuthView(TemplateView):

    template_name = "2fa/setup_2fa.html"

    def post(self, request):

        username = self.request.session['username']
        user = User.objects.get(username= username)
        context = {}
        try:
            two_factor_auth_data = user_two_factor_auth_data_create(user=user)
            context["otp_secret"] = two_factor_auth_data.otp_secret
            context["qr_code"] = two_factor_auth_data.generate_qr_code(name=user.username)
        except ValidationError as exc:
            context["form_errors"] = exc.messages

        return self.render_to_response(context)


class ConfirmTwoFactorAuthView(View):

    template_name = "2fa/confirm_2fa.html"
    success_url = reverse_lazy("index")
    form_class = OTPForm

    def get(self, request, *args, **kwargs):

        form = self.form_class
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):

        username = self.request.session['username']
        user = User.objects.get(username= username)
        form = OTPForm(request.POST)
        form.user = user
        if form.is_valid():
            form.two_factor_auth_data.rotate_session_identifier()
            self.request.session['2fa_token'] = str(form.two_factor_auth_data.session_identifier)
            login(self.request, user, backend = 'django.contrib.auth.backends.ModelBackend')
            return redirect("index")
        return render(request, self.template_name, {"form": form})



@method_decorator(login_required, name='dispatch')
class IndexView(View):

    def get(self, request, *args, **kwargs):

        if request.user.is_superuser:
            return redirect('admin:index')
        return redirect('list-customer')

@method_decorator(permissions_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class AddCustomerView(CreateView):

    form_class = CustomerForm
    template_name = "user/add.html"

    def form_valid(self, form):

        user = form.save()
        return redirect('sale-count', user.id)


@method_decorator(permissions_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UpdateCustomerView(UpdateView):

    model = Customer
    fields = ["name", "phone",  "active"]
    template_name = "user/update_customer.html"
    success_url = "/user/list-customer"

    def get_context_data(self, **kwargs):

        ctx = super(UpdateCustomerView, self).get_context_data(**kwargs)
        profiles_id = list(Sale.objects.filter(bill__customer=self.kwargs['pk']).values_list('profile_id', flat=True))
        uniques_ids = set(profiles_id)
        sales = []
        for id in uniques_ids:
            sale = Sale.objects.filter(bill__customer=self.kwargs['pk'], profile_id= id, cutted=False).last()
            if sale:
                sales.append(sale)
        for sale in sales:
            if sale:
                rest_days = getDifference(now, sale.date_limit, 'days')
                if rest_days < 0:
                    sale.rest_days = "Vencida"
                else:
                    sale.rest_days = rest_days
        ctx['sales'] = sales
        ctx['pk'] = self.kwargs['pk']
        return ctx


@method_decorator(login_required, name='dispatch')
class CustomerListView(ListView):

    model = Customer
    template_name = "user/list.html"

    def get_queryset(self, *args, **kwargs):

        customers = self.model.objects.filter(active=True)
        return customers



@method_decorator(login_required, name='dispatch')
@method_decorator(permissions_in_view, name='dispatch')
class AddUserView(CreateView):

    form_class = UserForm
    template_name = 'user/add_user.html'

    def form_valid(self, form):

        form.save()
        return redirect('list-user')

    def get_context_data(self, **kwargs):

        ctx = super(AddUserView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.POST or None)
        return ctx



@method_decorator(login_required, name='dispatch')
@method_decorator(permissions_in_view, name='dispatch')
class UserListView(ListView):

    model = User
    template_name = "user/user_list.html"

    def get_queryset(self, *args, **kwargs):

        users = self.model.objects.all()
        return users


class CustomerJson(BaseDatatableView):

    columns = ['Nombre', 'Telefono',  'Accion']
    order_columns = ['id']
    model = Customer
    #max_display_length = 500

    def get_initial_queryset(self):

        return self.model.objects.filter(active=True)


    def render_column(self, row, column):
        return super(CustomerJson, self).render_column(row, column)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            q = Q(phone__icontains=search) | Q(name__icontains=search)
            qs = qs.filter(q)

        return qs

    def prepare_results(self, qs):

        permissions = my_permissions(self.request.user)
        json_data = []
        if 'change_customer' in permissions and 'delete_customer'  in permissions:
            for item in qs:
                link1 = f'<a href="/count/sale/{item.id}"><button type="button" class ="btn btn-primary btn-icon-text" ><i class ="mdi mdi-square-inc-cash"></i>Vender</button></a>'
                link2 = f'<a href="/user/update-customer/{item.id}"><button type="button" class="btn btn-info  btn-icon-text"><i class="mdi mdi-information"></i>Planes</button></a>'
                link3 = f'<a href="/user/delete-customer/{item.id}"><button type="button" class="btn btn-danger  btn-icon-text"><i class="mdi mdi-delete-forever"></i>Eliminar</button></a>'
                json_data.append([
                    item.id,
                    item.name,
                    str(item.phone),
                    link1,
                    link2,
                    link3
                ])
        elif not 'change_customer' in permissions and 'delete_customer' in permissions:
            for item in qs:
                link1 = f'<a href="/count/sale/{item.id}"><button type="button" class ="btn btn-primary btn-icon-text" ><i class ="mdi mdi-square-inc-cash"></i>Vender</button></a>'
                link2 = f'<a href="/user/delete-customer/{item.id}"><button type="button" class="btn btn-danger  btn-icon-text"><i class="mdi mdi-delete-forever"></i>Eliminar</button></a>'
                json_data.append([
                    item.id,
                    item.name,
                    str(item.phone),
                    link1,
                    link2
                ])
        elif 'change_customer' in permissions and not 'delete_customer' in permissions:
            for item in qs:
                link1 = f'<a href="/count/sale/{item.id}"><button type="button" class ="btn btn-primary btn-icon-text" ><i class ="mdi mdi-square-inc-cash"></i>Vender</button></a>'
                link2 = f'<a href="/user/update-customer/{item.id}"><button type="button" class="btn btn-info  btn-icon-text"><i class="mdi mdi-information"></i>Planes</button></a>'
                json_data.append([
                    item.id,
                    item.name,
                    str(item.phone),
                    link1,
                    link2
                ])
        else:
            for item in qs:
                link1 = f'<a href="/count/sale/{item.id}"><button type="button" class ="btn btn-primary btn-icon-text" ><i class ="mdi mdi-square-inc-cash"></i>Vender</button></a>'
                json_data.append([
                    item.id,
                    item.name,
                    str(item.phone),
                    link1
                ])

        return json_data


class CustomerDeleteView(DeleteView):

    model = Customer
    success_url = reverse_lazy("list-customer")


@method_decorator(login_required, name='dispatch')

class ProfileNextExpiredView(ListView):

    model = Sale
    template_name = "user/list-to-expire.html"

    def get_queryset(self,  *args, **kwargs):

        date_init = datetime.datetime.now()
        date_finish = datetime.datetime.now() + datetime.timedelta(days=3)
        date_init = date_init.strftime("%Y-%m-%d")
        date_finish = date_finish.strftime("%Y-%m-%d")
        sales_to_expires = self.model.objects.filter(profile__saled=True, renovated=False, cutted=False, date_limit__range=[date_init , date_finish ]).order_by('date_limit')
        for sale in sales_to_expires:
            rest_days = getDifference( sale.date_limit.date(), now.date(),  'days')
            sale.rest_days = -rest_days
        return sales_to_expires


    def post(self, request, *args, **kwargs):


        counts = {}
        for item in request.POST:
            if item.isnumeric():
                if request.POST[item] == 'on':
                    sale = Sale.objects.filter(id=item).last()
                    sale.renovated=True
                    sale.save()
                    bill = Bill.objects.create(customer_id=sale.bill.customer.id, saler=request.user, total=0)
                    date_limit = CalculateDateLimit(sale.date_limit, int(request.POST['months']))
                    request.user.sale_profile(sale.profile, int(request.POST['months']), date_limit, bill)
                    message_renew(sale.profile, bill.customer, date_limit)

        subtotal = Price.objects.filter(platform=sale.profile.count.platform, num_profiles=1 ).first()
        bill.total =  subtotal.price *int(request.POST['months'])
        bill.save()
        return redirect('bill-list')

@method_decorator(login_required, name='dispatch')
class ProfileExpiredView(ListView):

    model = Sale
    template_name = "user/list-expired.html"

    def get_queryset(self,  *args, **kwargs):

        date_finish = datetime.datetime.now().date()# - datetime.timedelta(days=0)
        sale_expired = self.model.objects.filter(profile__saled=True, renovated=False, cutted=False).extra(where=["DATE(date_limit) < %s"], params=[date_finish]).order_by('-date_limit')
        print(len(sale_expired))
        for sale in sale_expired:
            sale.date_limit = sale.date_limit.date()
            rest_days = getDifference(sale.date_limit, now.date(), 'days')
            sale.rest_days = -rest_days
        return sale_expired

    def get_context_data(self,**kwargs):
        context = super(ProfileExpiredView,self).get_context_data(**kwargs)
        context['now'] = datetime.datetime.now()
        return context

class SendMessagesWhatsappApi(View) :

    def get(self, request, *args, **kwargs):
        counts = []
        payload = Customer.get_phones_for_messages( Sale)
        for  data in payload:
            message = f"Hola, {payload[data]['name']} tu servicio  {payload[data]['platform']}\n" \
                      f" 👤USUARIO: {payload[data]['email']} \n" \
                      f" 🔐CONTRASEÑA: {payload[data]['password']}  \n" \
                      f" {payload[data]['days']}  \n" \
                      f" Avísame si lo vas a renovar. Muchas gracias 🙂"
            counts.append([payload[data]['name'], payload[data]['email']])
            send_message(payload[data]['phone'], message)
        return JsonResponse(payload)



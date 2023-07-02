from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import View #PARA VISTAS GENERICAS
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Customer
from count.models import Sale, Bill
from .forms import CustomerForm, UserForm
from count.decorators import usertype_in_view, check_user_type
from django.contrib.auth.models import User
from .whatsapp_api import send_message
import datetime, pytz
from count.libraries import getDifference
from django.contrib import messages

utc = pytz.UTC
now = datetime.datetime.now()
now = now.replace(tzinfo=utc)


def context_app(request):

    context = {}
    user_type = check_user_type(request)

    if request.user.is_authenticated:

            context['user_type'] = user_type


    return context

@method_decorator(login_required, name='dispatch')
class IndexView(View):

    def get(self, request, *args, **kwargs):

        if request.user.is_superuser:
            return redirect('admin:index')
        return redirect('list-customer')


@method_decorator(login_required, name='dispatch')
class AddCustomerView(CreateView):

    form_class = CustomerForm
    template_name = "user/add.html"

    def form_valid(self, form):

        user = form.save()
        return redirect('sale-count', user.id)


@method_decorator(usertype_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UpdateCustomerView(UpdateView):

    model = Customer
    fields = ["name", "phone",  "active"]
    template_name = "user/update_customer.html"
    success_url = "/user/list-customer"

    def get_context_data(self, **kwargs):

        buys = []
        ctx = super(UpdateCustomerView, self).get_context_data(**kwargs)

        sales = Sale.objects.filter(bill__customer=self.kwargs['pk'])
        for sale in sales:
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
@method_decorator(usertype_in_view, name='dispatch')
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
@method_decorator(usertype_in_view, name='dispatch')
class UserListView(ListView):

    model = User
    template_name = "user/user_list.html"

    def get_queryset(self, *args, **kwargs):

        users = self.model.objects.all()
        return users

@method_decorator(login_required, name='dispatch')
class SendMessagesWhatsappApi(View) :

    def get(self, request, *args, **kwargs):

        date_ago = now + datetime.timedelta(days=3)
        payload = Customer.get_phones_for_messages( Sale, now, date_ago)
        for data in payload:
            message = f"Hola, tu servicio  \n" \
                      f" 👤USUARIO: {data['email']} \n" \
                      f"🔐CONTRASEÑA: {data['password']}  \n" \
                      f" Se vence dentro de: {data['remaining_days']} día (s) \n" \
                      f" Avísame si lo vas a renovar. Muchas gracias 🙂"
            data['response'] = send_message(data['phone'], message)
        return HttpResponse(payload)

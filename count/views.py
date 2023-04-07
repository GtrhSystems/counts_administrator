from django.shortcuts import render, redirect, get_object_or_404
from django.views import View  # PARA VISTAS GENERICAS
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView
from .forms import SaleForm
from .models import Profile, Sale, Count
from user.models import Customer
from django.http import HttpResponse, JsonResponse
from django.core import serializers

@method_decorator(login_required, name='dispatch')
class DashboardView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard.html')


@method_decorator(login_required, name='dispatch')
class AddSaleView(View):

    form_class = SaleForm
    template_name = "sale/add.html"

    def get(self, request, *args, **kwargs):

        customer = Customer.objects.filter(id= kwargs['id']).first()
        if customer:
            return render(request, self.template_name, { 'form': self.form_class, 'customer':customer })
        else:
            return redirect('index')


    def post(self, request, *args, **kwargs):

        form = self.form_class (request.POST)
        customer = Customer.objects.filter(id= kwargs['id']).first()
        if customer and form.is_valid():
            profile = Profile.search_profile_no_saled(request.POST['platform'])
            count = request.user.sale_profile(customer, profile, int(request.POST['months']))
            return render(request, 'sale/sale_post.html', { 'count':count })
        return render(request, self.template_name, {'form': self.form_class, 'customer': customer})

@method_decorator(login_required, name='dispatch')
class SalerListView(ListView):

    model = Sale
    template_name = "sale/list.html"

    def get_queryset(self,  *args, **kwargs):

        sales = self.model.objects.filter(saler=self.request.user)
        return sales


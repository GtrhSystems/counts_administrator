from django.shortcuts import render, redirect, get_object_or_404
from django.views import View #PARA VISTAS GENERICAS
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView
from .models import Customer
from .forms import CustomerForm, UserForm


@method_decorator(login_required, name='dispatch')
class IndexView(View):

    def get(self, request, *args, **kwargs):

        return render(request, 'index.html' )


@method_decorator(login_required, name='dispatch')
class AddView(CreateView):

    form_class = CustomerForm
    template_name = "user/add.html"


    def form_valid(self, form):

        form.save()
        return redirect('index')


@method_decorator(login_required, name='dispatch')
class UserListView(ListView):

    model = Customer
    template_name = "user/list.html"

    def get_queryset(self, *args, **kwargs):

        customers = self.model.objects.filter(active=True)
        return customers
        


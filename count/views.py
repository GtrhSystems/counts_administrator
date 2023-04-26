from django.shortcuts import render, redirect, get_object_or_404
from django.views import View  # PARA VISTAS GENERICAS
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .decorators import usertype_in_view
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .forms import SaleForm, GetInterDatesForm, CountForm, CreatePromotionForm, PlatformForm, CreatePlatformForm
from .models import Profile, Sale, Count, Platform, Promotion, PromotionPlatform
from user.models import Customer
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.conf import settings
from django.contrib.auth.models import User
from count.decorators import usertype_in_view, check_user_type


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
                                         password = request.POST['password'])
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
        form.save()
        return redirect('platform-list')


@method_decorator(usertype_in_view, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UpdatePlatformView(UpdateView):

    model = Platform
    fields = ["name", "logo", "price", "active"]
    template_name = "platform/update.html"
    success_url = "/count/platform/list"



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

        counts = self.model.objects.all().order_by('-date')
        return counts


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
            return render(request, 'sale/sale_post.html', { 'profile':profile })
        return render(request, self.template_name, {'form': self.form_class, 'customer': customer})

@method_decorator(login_required, name='dispatch')
class SalesListView(ListView):

    model = Sale
    template_name = "sale/list.html"

    def get_queryset(self,  *args, **kwargs):

        sales = self.model.objects.filter(saler=self.request.user)
        return sales

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
class InterdatesSalesView(ListView):

    model = Sale
    template_name = "sale/list-no-layout.html"

    def get_queryset(self, *args, **kwargs):
        print(kwargs)
        if 'user' in kwargs:
            user = User.objects.filter(username = kwargs['user'])
        else:
            user = self.request.user

        sales = self.model.GetInterdatesSales(user, self.kwargs['initial_date'],
                                                  self.kwargs['final_date'] )
        return sales

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
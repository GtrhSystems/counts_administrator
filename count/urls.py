from django.urls import include, path
from count import views

urlpatterns = [
        path('accounts/', include('django.contrib.auth.urls')),
        path('', views.DashboardView.as_view(), name='dashboard'),
        path('sale/<int:id>', views.AddSaleView.as_view(), name='sale-count'),
        path('sales/list', views.SalerListView.as_view(), name='sale-list'),



]
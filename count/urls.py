from django.urls import include, path
from count import views

urlpatterns = [

        path('', views.DashboardView.as_view(), name='dashboard'),
        path('sale/<int:id>', views.AddSaleView.as_view(), name='sale-count'),
        path('sales/list', views.SalesListView.as_view(), name='sale-list'),
        path('inter-dates/<str:model>', views.InterDatesView.as_view(), name='inter-dates'),
        path('sales/<str:initial_date>/<str:final_date>', views.InterdatesSalesView.as_view(), name='interdates-sales-list'),
        path('services/cron-whatsapp', views.CronWhatsappView.as_view(), name='cron-whatsapp'),




]
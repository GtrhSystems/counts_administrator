from django.urls import include, path
from count import views

urlpatterns = [

        path('', views.DashboardView.as_view(), name='dashboard'),
        path('sale/<int:id>', views.AddSaleView.as_view(), name='sale-count'),
        path('bill/list', views.BillListView.as_view(), name='bill-list'),
        path('sales/list/<int:id>', views.SalesListView.as_view(), name='sale-list'),
        path('inter-dates/<str:model>', views.InterDatesView.as_view(), name='inter-dates'),
        path('<str:user>/inter-dates/<str:model>', views.InterDatesView.as_view(), name='inter-dates-saler'),
        path('sales/<str:initial_date>/<str:final_date>', views.InterdatesSalesView.as_view(), name='interdates-sales-list'),
        path('sales/<str:user>/<str:initial_date>/<str:final_date>', views.InterdatesSalesView.as_view(), name='interdates-sales-saler-list'),
        path('services/cron-whatsapp', views.CronWhatsappView.as_view(), name='cron-whatsapp'),
        path('create', views.CreateCount.as_view(), name='create-count'),
        path('create-pins-profiles/<str:platform>', views.CreatePinsProfiles.as_view(), name='create-pins-profiles'),
        path('list', views.CountsListView.as_view(), name='count-list'),
        #promotions
        path('promotion/create', views.CreatePromotionView.as_view(), name='create-promotion'),
        path('promotion/list', views.ListPromotionView.as_view(), name='list-promotion'),
        path('promotion/sale/<int:user_id>/<int:promotion_id>', views.SalePromotionView.as_view(), name='sale-promotion'),

        path('platform/create', views.AddPlatformView.as_view(), name='create-platform'),
        path('platform/update/<int:pk>', views.UpdatePlatformView.as_view(), name='update-platform'),
        path('platform/list', views.PlatformListView.as_view(), name='platform-list'),
        path('platform/set-prices_by-profiles/<int:quantity>', views.SetPricesOfQuantityProfilesView.as_view(), name='set-prices_by-profiles'),


        #path('sale/add-renovation/<int:pk>', views.AddRenovationView.as_view(), name='add-renovation'),
        path('get-profiles-available/<str:platform>', views.GetProfilesAvailableView.as_view(), name='get-profiles-available'),









]
from django.urls import include, path
from count import views

urlpatterns = [

        path('', views.DashboardView.as_view(), name='dashboard'),

        # sales
        path('select-plan-by-platform/<int:platform_id>', views.SelectPlan.as_view(), name='select-plan-by-platform'),
        # path('sale/add-renovation/<int:pk>', views.AddRenovationView.as_view(), name='add-renovation'),
        path('get-profiles-available/<str:platform>', views.GetProfilesAvailableView.as_view(),
             name='get-profiles-available'),
        path('get-profiles-available/plan/<str:plan>', views.GetProfilesAvailableView.as_view(),
             name='get-profiles-available'),
        path('sale/<int:id>', views.AddSaleView.as_view(), name='sale-count'),
        path('bill/list', views.BillListView.as_view(), name='bill-list'),
        path('sales/list/<int:id>', views.SalesListView.as_view(), name='sale-list'),
        path('inter-dates/<str:model>', views.InterDatesView.as_view(), name='inter-dates'),
        path('<str:user>/inter-dates/<str:model>', views.InterDatesView.as_view(), name='inter-dates-saler'),
        path('sales/<str:initial_date>/<str:final_date>', views.InterdatesSalesView.as_view(), name='interdates-sales-list'),
        path('sales/<str:user>/<str:initial_date>/<str:final_date>', views.InterdatesSalesView.as_view(), name='interdates-sales-saler-list'),
        path('sale/cancel-sale/<int:id>', views.CancelSaleView.as_view(), name='cancel-sale'),
        path('sale/search', views.SearchSaleView.as_view(), name='search-sale'),
        path('change-profile-sale/<int:pk>', views.ChangeProfileSaleView.as_view(), name='change-profile-sale'),


        path('services/cron-whatsapp', views.CronWhatsappView.as_view(), name='cron-whatsapp'),

        # platforms
        path('platform/create', views.AddPlatformView.as_view(), name='create-platform'),
        path('platform/update/<int:pk>', views.UpdatePlatformView.as_view(), name='update-platform'),
        path('platform/list', views.PlatformListView.as_view(), name='platform-list'),
        path('platform/set-prices_by-profiles/<int:quantity>', views.SetPricesOfQuantityProfilesView.as_view(), name='set-prices_by-profiles'),


        #count
        path('create', views.CreateCount.as_view(), name='create-count'),
        path('update/<int:id>', views.UpdateCount.as_view(), name='update-count'),
        path('create-pins-profiles/<str:type>/<int:id>', views.CreatePinsProfiles.as_view(), name='create-pins-profiles'),
        path('list', views.CountsListView.as_view(), name='count-list'),
        path('list-ajax', views.CountListAjax.as_view(), name='count-list-ajax'),
        path('cut-profile/<int:sale_id>/<int:id>', views.CutProfileView.as_view(), name='cut-profile'),
        path('owner-profile/<int:sale_id>/<int:id>', views.OwnerProfileView.as_view(), name='owner-profile'),

        # plan
        path('plan/create/<str:platform>', views.CreatePlan.as_view(), name='create-plan'),
        path('plan/update/<int:pk>', views.UpdatePlanView.as_view(), name='update-plan'),
        path('plan/list/<str:template_name>/<str:platform>', views.PlanListView.as_view(), name='plan-list'),

        #counts
        path('edit-count-data/<str:type>/<int:id>', views.EditCountDataView.as_view(), name='edit-count-data'),
        path('edit-sale-data/<int:id>', views.EditSaleDataView.as_view(), name='edit-sale-data'),
        path('change-date-limit/<int:id>', views.ChangeDateLimitView.as_view(), name='change-date-limit'),

        path('<pk>/delete/', views.CountDeleteView.as_view(), name='delete-count'),
        path('send-whatsapp-message', views.SendMessageWhatsapp.as_view(), name='send-whatsapp-message'),
        path('send-plan-whatsapp-message', views.SendPlanMessageWhatsapp.as_view(), name='send-plan-whatsapp-message'),
        path('send-whatsapp-expired', views.SendMessageWhatsappExpired.as_view(), name='send-whatsapp-expired'),
        path('list-to-expire', views.CountNextExpiredView.as_view(), name='count-list-to-expire'),
        path('list-expired', views.CountExpiredView.as_view(), name='count-list-expired'),
        path('change-password/<str:type>/<int:id>', views.ChangeTypePasswordView.as_view(), name='change-password-type'),



        #promotions
        path('promotion/create', views.CreatePromotionView.as_view(), name='create-promotion'),
        path('promotion/list', views.ListPromotionView.as_view(), name='list-promotion'),
        path('promotion/sale/<int:user_id>/<int:promotion_id>', views.SalePromotionView.as_view(), name='sale-promotion'),













]

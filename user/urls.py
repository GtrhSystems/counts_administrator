from django.urls import include, path
from user import views
from django.conf import settings

urlpatterns = [
        path('', views.IndexView.as_view(), name='index'),
        path('add-customer', views.AddCustomerView.as_view(), name='add-customer'),
        path('update-customer/<int:pk>', views.UpdateCustomerView.as_view(), name='update-customer'),
        path('list-customer', views.CustomerListView.as_view(), name='list-customer'),
        path('list-customer/ajax', views.CustomerJson.as_view(), name='list-customer-ajax'),
        path('add-user', views.AddUserView.as_view(), name='add-user'),
        path('list-user', views.UserListView.as_view(), name='list-user'),
        path('send-message', views.SendMessagesWhatsappApi.as_view(), name='send-message'),

        path('list-to-expire', views.ProfileNextExpiredView.as_view(), name='list-to-expire'),
        path('list-expired', views.ProfileExpiredView.as_view(), name='list-expired'),
        path('delete-customer/<pk>', views.CustomerDeleteView.as_view(), name='delete-customer'),

        # 2fa
        path("setup-2fa", views.SetupTwoFactorAuthView.as_view(), name="setup-2fa"),
        path("confirm-2fa/", views.ConfirmTwoFactorAuthView.as_view(), name="confirm-2fa"),

]

if settings.OPT_ACTIVE:
   urlpatterns = urlpatterns +   [ path('login/', views.MyLoginView.as_view(), name='login-otp')]
else:
   urlpatterns = urlpatterns +   [ path('accounts/', include('django.contrib.auth.urls'))]

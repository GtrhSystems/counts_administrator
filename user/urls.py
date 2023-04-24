from django.urls import include, path
from user import views

urlpatterns = [
        path('accounts/', include('django.contrib.auth.urls')),
        path('', views.IndexView.as_view(), name='index'),
        path('add-customer', views.AddCustomerView.as_view(), name='add-customer'),
        path('list-customer', views.CustomerListView.as_view(), name='list-customer'),
        path('add-user', views.AddUserView.as_view(), name='add-user'),
        path('list-user', views.UserListView.as_view(), name='list-user'),
]
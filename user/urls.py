from django.urls import include, path
from user import views

urlpatterns = [
        path('accounts/', include('django.contrib.auth.urls')),
        path('', views.IndexView.as_view(), name='index'),
        path('add', views.AddView.as_view(), name='add-user'),
        path('list', views.UserListView.as_view(), name='list-user'),
]
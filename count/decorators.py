from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.urls import resolve

PERMISSION_BY_VIEW = {
    'update-platform' : ['change_platform'],
    'add-customer' : ['add_customer'],
    'update-customer' : ['change_customer'],
    'add-user' : ['add_user'],
    'create-count': ['add_count'],
    'edit-count-data': ['change_count'],
    'delete-count': ['delete_count'],
    'change-date-limit': ['change_count'],
    'create-promotion': ['add_promotion'],
    'sale-count': ['add_sale'],
    'edit-sale-data':  ['change_count'],
    'create-pins-profiles':  ['add_count'],
    'cut-profile': ['change_count'],

}

def my_permissions(user):

    permissions = list(user.user_permissions.all().values_list('codename', flat=True))
    return permissions


def permissions_in_view(function):

    def wrap(request, *args, **kwargs):

        permissions = my_permissions(request.user)
        request_url = request.__dict__['path_info'] #captura todo el request en un dict
        match = resolve(request_url) #devuelve el name de la vista
        url_name = match.url_name
        for permission in permissions:
            if permission  in PERMISSION_BY_VIEW[url_name]:
                return function(request, *args, **kwargs)
        raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap



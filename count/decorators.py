from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.urls import resolve

def check_user_type(request):    

    if request.user.is_superuser:
        user_type = "superuser"
    elif request.user.is_staff:
        user_type = "staff"
    else:
        user_type = "saler"
    return user_type                



def usertype_in_view(function):

    def wrap(request, *args, **kwargs):
        superuser = ['add-user',
                     'list-user',
                     'create-count',
                     'create-pins-profiles',
                     'count-list',
                     'count-list-ajax',
                     'create-promotion',
                     'create-platform',
                     'update-platform',
                     'platform-list',
                     'update-customer',
                     'set-prices_by-profiles',
                     'list-to-expire',
                     'reactivate-profile',
                     'edit-count-data',
                     'count-list-expired',
                     'count-list-to-expire',
                     'change-date-limit',
                     ]

        staff = ['add-user',
                 'create-count',
                 'create-pins-profiles',
                 'count-list',
                 'count-list-ajax',
                 'create-promotion',
                 'list-to-expire',
                 'reactivate-profile',
                 'edit-count-data',
                 'update-customer',
                 'create-platform',
                 'delete-count',
                 'list-expired',
                 'count-list-expired',
                 'count-list-to-expire',
                 'change-date-limit',
                 ]

        saler = ['add-user'

                 ]

        request_url = request.__dict__['path_info'] #captura todo el request en un dict
        match = resolve(request_url) #devuelve el name de la vista
        url_name = match.url_name
        user_type = check_user_type(request)
        if url_name  in eval(user_type):
            return function(request, *args, **kwargs)        
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap



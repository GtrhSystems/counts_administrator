from django.contrib import admin
from django.contrib.auth.models import User, Permission


admin.site.site_header = "El Gamer Mexicano  Administrador"
admin.site.site_title = "El Gamer Mexicano  Administrador"
admin.site.index_title = "Bienvenidos al portal de administración El Gamer Mexicano "


PERMISSIONS_ACTIVES = [
    'change_platform',
    'add_customer',
    'change_customer',
    'add_user',
    'add_count',
    'change_count',
    'delete_count',
    'change_count',
    'add_promotion',
    'delete_sale',
    'add_sale',
    'add_plan',
    'change_plan',
]

class UserAdmin(admin.ModelAdmin):

    list_display = ('username', 'is_active', 'first_name', 'last_name', 'email')
    #fields = ['first_name', 'last_name', 'email',  'is_active']
    fieldsets = (
        ('Información personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos de usuario', {'fields': ( 'last_login', 'user_permissions')}),
    )
    #readonly_fields = ['first_name', 'last_name', 'email']
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username__startswith', 'email__startswith')
    filter_horizontal = ('groups', 'user_permissions',)
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "user_permissions":
            kwargs["queryset"] = Permission.objects.filter(codename__in=PERMISSIONS_ACTIVES)
        return super().formfield_for_manytomany(db_field, request, **kwargs)



admin.site.unregister(User)
admin.site.register(User, UserAdmin)
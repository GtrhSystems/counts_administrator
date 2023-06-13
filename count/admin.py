from django.contrib import admin
from .models import Platform, Price ,Count

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
   list_display = ( 'name','logo','num_profiles', 'active' )
   fields  = ['name', 'logo', 'num_profiles' ,'active']
   list_filter = ('name','active') #se aplican filtros por estos dos campos


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
   list_display = ( 'platform','num_profiles','price')
   fields  = ['platform', 'num_profiles', 'price' ]
   list_filter = ('platform','num_profiles') #se aplican filtros por estos dos campos


@admin.register(Count)
class CountAdmin(admin.ModelAdmin):
   list_display = ( 'email','platform','password' )
   fields  = ['platform','email', 'password' ]
   list_filter = ('platform','email')


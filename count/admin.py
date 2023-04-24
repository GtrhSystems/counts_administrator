from django.contrib import admin
from .models import Platform, Count

#@admin.register(Platform)
#class PlatformAdmin(admin.ModelAdmin):
#   list_display = ( 'name','logo','num_profiles', 'active' )
#   fields  = ['name', 'logo', 'num_profiles' ,'active']
#   list_filter = ('name','active') #se aplican filtros por estos dos campos

#@admin.register(Count)
#class CountAdmin(admin.ModelAdmin):
#   list_display = ( 'email','platform','password', 'pin' )
#   fields  = ['platform','email', 'password' ,'pin']
#   list_filter = ('platform','email') #se aplican filtros por estos dos campos


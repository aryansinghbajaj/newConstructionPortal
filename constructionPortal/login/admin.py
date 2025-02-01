from django.contrib import admin
from .models import UserRegistration, PreRegisteredUser, UserGroup

class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class PreRegisteredUserAdmin(admin.ModelAdmin):
    list_display = ('userid', 'email', 'password_sent', 'group')
    search_fields = ('userid', 'email')
    list_filter = ('group',)
    fields = ('userid', 'email', 'password_sent', 'group')

class UserRegistrationAdmin(admin.ModelAdmin):
    list_display = ('userid', 'name', 'email', 'group')
    search_fields = ('userid', 'name', 'email')
    list_filter = ('group',)

admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(PreRegisteredUser, PreRegisteredUserAdmin)
admin.site.register(UserRegistration, UserRegistrationAdmin)
from django.contrib import admin
from .models import UserRegistration, PreRegisteredUser

class PreRegisteredUserAdmin(admin.ModelAdmin):
    list_display = ('userid', 'email', 'password_sent')
    search_fields = ('userid', 'email')
    fields = ('userid', 'email', 'password_sent')

class UserRegistrationAdmin(admin.ModelAdmin):
    list_display = ('userid', 'name', 'email')
    search_fields = ('userid', 'name', 'email')

# Register each model only once
admin.site.register(PreRegisteredUser, PreRegisteredUserAdmin)
admin.site.register(UserRegistration, UserRegistrationAdmin)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from home.models import Profile, Account,Privilege,Appointment,Requests,PendingProfileUpdate

admin.site.register(Profile)
admin.site.register(Appointment)
admin.site.register(Privilege)
admin.site.register(Account)
admin.site.register(Requests)
admin.site.register(PendingProfileUpdate)

# Register your models here.

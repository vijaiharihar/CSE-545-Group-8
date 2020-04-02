from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from home import models

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = models.Appointment
        fields=('appointment_date','appointment_subject',)

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = models.PendingProfileUpdate
        fields=('first_name', 'last_name','street_address','city','state','zip_code',)

class AccountForm(forms.ModelForm):
    class Meta:
        model = models.Account
        fields=('account_type',)

class AccountDeleteForm(forms.Form):
    account_number=forms.IntegerField()
        
"""Secure_Bank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from . import views
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

app_name = "user_home"

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('logout/',views.user_logout,name='logout'),
    path('appointment/',views.appointment,name='appointment'),
    path('profile_update/',views.updateProfile, name='profile'),
    path('new_account/',views.newAccount, name='new_account'),
    path('delete_account/',views.deleteAccount, name='delete_account'),
    path('deposit/',views.default_fund_deposit, name='deposit'),
    path('withdraw/',views.default_fund_withdraw, name='withdraw'),
    path('getStatement/',views.default_get_statements, name='getStatement'),
    path('fundTransfer/',views.default_fund_transfer, name='transfer')
]

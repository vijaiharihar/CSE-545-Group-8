from django.urls import path
from . import views
from django.conf.urls import url

app_name = "home"

urlpatterns = [
    path('', views.homepage, name = 'create_account_homepage'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('phone_otp', views.phone_otp, name = 'phone_otp'),
]


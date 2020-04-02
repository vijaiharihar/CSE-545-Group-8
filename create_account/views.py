from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import ExtendedUserCreationForm, UserProfileForm, AccountForm, Otp
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from home.models import Privilege
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.encoding import force_text
from django.conf import settings
from random import randint
import time
import logging

log = logging.getLogger(__name__)


def homepage(request):
    global mail_expiry
    global otp_expiry
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        account_form = AccountForm(request.POST)
        if form.is_valid() and profile_form.is_valid() and account_form.is_valid():
            user = form.save()
            user.save()
            acc = account_form.save(commit=False)
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.privilege_id = Privilege.objects.get(user_type="Customer")
            acc.user = profile.user
            profile.save()
            acc.save()
            current_site = get_current_site(request)
            request.session['mobile_number'] = profile.mobile_number
            request.session['token'] = randint(10000, 99999)
            request.session['user'] = user.username
            mail_subject = 'Activate your bank account.'
            message = render_to_string('acc_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
                'token': force_text(account_activation_token.make_token(user)),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            mail_expiry = time.time()
            email.send()
            return HttpResponseRedirect('/login/')
    else:
        form = ExtendedUserCreationForm()
        profile_form = UserProfileForm()
        account_form = AccountForm()

    context = {'form': form, 'profile_form': profile_form, 'account_form': account_form}
    return render(request, 'create_account/register.html', context)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if mail_expiry - time.time() > 86400:
        user.delete()
        return HttpResponse('Activation link has expired!')
    if user is not None and account_activation_token.check_token(user, token):
        user_instance = User.objects.get(username=request.session['user'])
        user_instance.is_active = True
        user_instance.save()
        return HttpResponseRedirect('/login')
    else:
        user.delete()
        return HttpResponse('Activation link is invalid!')


def phone_otp(request):
    otp_expiry = time.time()
    user_instance = User.objects.get(username=request.session['user'])
    if request.method == 'POST':
        form = Otp(request.POST)
        if form.is_valid():
            if time.time() - otp_expiry > 300:
                user_instance.delete()
                return HttpResponse("Registration Failed!! OTP expired")
            if form.cleaned_data['otp'] == request.session['token']:
                user_instance.is_active = True
                user_instance.save()
                return HttpResponseRedirect('/login')
        user_instance.delete()
        return HttpResponse("Registration Failed!! Wrong OTP")
    else:
        form = Otp()
        context = {'form': form}
        return render(request, 'phone_otp/phone_otp.html', context)

# Create your views here.

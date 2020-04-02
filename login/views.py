from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from datetime import datetime
from create_account import forms
from home.models import User,Profile
from .forms import LoginForm,Otp,Token,Forgot_password
import time
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.encoding import force_text
from random import randint
from django.urls import reverse
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
import logging
log = logging.getLogger(__name__)
from django.conf import settings
from home import models


#try wrong account list ------ username: number of try
block_wait_list={}
#blcok list -------username: start time
block_list={}


def login_user(request):
    global block_wait_list
    global block_list
    global otp_expiry
    try_times=0
    if request.method=='POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            userObj = authenticate(username=form.cleaned_data['user_id'], password=form.cleaned_data['password'])
            request.session['username'] = form.cleaned_data['user_id']
            request.session['password'] = form.cleaned_data['password']
            user_instance=User.objects.get(username=form.cleaned_data['user_id'])
            profile_instance=Profile.objects.get(user=user_instance)
            #check block list
            if form.cleaned_data['user_id'] in block_list:
                #check block time
                start_time=block_list[form.cleaned_data['user_id']]
                end_time=time.time()
                if ((start_time != 0) & (end_time - start_time <= 600)):
                    #return to block page
                    return login_block(request)

            #login#delete user in block list
                if form.cleaned_data['user_id'] in block_list:
                    block_list.pop(form.cleaned_data['user_id'])
                if form.cleaned_data['user_id'] in block_wait_list:
                    block_wait_list.pop(form.cleaned_data['user_id'])
                #return user home page

            elif userObj is None or profile_instance.flag==False or user_instance.is_active==False:
                #not in block list add
                if form.cleaned_data['user_id'] in block_wait_list:
                    try_times=block_wait_list[form.cleaned_data['user_id']]
                    block_wait_list[form.cleaned_data['user_id']] = try_times + 1
                else:
                    block_wait_list[form.cleaned_data['user_id']] = 1
                #check try times
                #start block
                if(try_times>=3):
                    #add block time
                    start_time=time.time()
                    block_list[form.cleaned_data['user_id']]=start_time
                    block_wait_list.pop(form.cleaned_data['user_id'])
                    return login_block(request)
            #if authorization is successful, redirect to appropriate page
            #return HttpResponseRedirect('/')
            elif userObj is not None and profile_instance.flag==True and user_instance.is_active:
                token=randint(10000,99999)
                to_email=user_instance.email
                mail_subject = 'Login OTP'
                message = render_to_string('authenticate_otp.html', {
                'user': request.user,
                'otp' : token
                 })
                email = EmailMessage(
                            mail_subject,message, to=[to_email]
                )
                email.send()
                otp_expiry=time.time()
                request.method='GET'
                request.session['token'] = token
                return verify_otp(request)
        return HttpResponse("Login Failed!!")

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form':form})

def login_block(request):
    return HttpResponse("Login block!! Wait for 10 minutes")

def verify_otp(request):
    trials=0
    userObj = authenticate(username=request.session['username'], password=request.session['password'])
    if request.method == 'POST':
        form = Otp(request.POST)
        if form.is_valid():
            if time.time()-otp_expiry>300:
                return HttpResponse("Login Failed!! OTP expired")
            if form.cleaned_data['otp'] == request.session['token']:
                login(request,userObj)
                request.session['last_activity'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                return HttpResponseRedirect('/user_home/')
            else:
                if request.session['username'] in block_list:
                    #check block time
                    start_time=block_list[request.session['username']]
                    end_time=time.time()
                    if ((start_time != 0) & (end_time - start_time <= 600)):
                        return login_block(request)

                #login#delete user in block list
                    if request.session['username'] in block_list:
                        block_list.pop(request.session['username'])
                    if request.session['username'] in block_wait_list:
                        block_wait_list.pop(request.session['username'])
                    #return user home page

                else:
                    #not in block list add
                    if request.session['username'] in block_wait_list:
                        trials=block_wait_list[request.session['username']]
                        block_wait_list[request.session['username']] = trials + 1
                    else:
                        block_wait_list[request.session['username']] = 1
                    #check try times
                    #start block
                    if(trials>=3):
                        #add block time
                        start_time=time.time()
                        block_list[request.session['username']]=start_time
                        block_wait_list.pop(request.session['username'])
                        return login_block(request)

        return HttpResponse("Login Failed!! Wrong OTP")
    else:
        form = Otp()
    context={'form' : form}
    return render(request,'enter_otp.html',context)

def forgot_password(request):
    if request.method == 'POST':
        form = Forgot_password(request.POST)
        if form.is_valid():
            user_instance=User.objects.get(username=form.cleaned_data['username'])
            print(validate_password(form.cleaned_data['new_password']))
            if (user_instance != None) and (user_instance.email==form.cleaned_data['email']):
                if validate_password(form.cleaned_data['new_password'])==None and form.cleaned_data['new_password']==form.cleaned_data['confirm_new_password']:
                    user_instance.password=make_password(form.cleaned_data["new_password"])  
                    user_instance.save()
                    return HttpResponseRedirect('/login')
        return HttpResponse("Incorrect details")
    else:
        form = Forgot_password()
        context={'form' : form}
        return render(request,'forgot_password.html',context)
    return HttpResponse("Try again")


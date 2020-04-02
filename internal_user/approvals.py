from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from home.models import Privilege
from home.models import Profile
from home.models import Account
from django.contrib.auth.models import User
from home.models import PendingProfileUpdate


def getUnapprovedProfiles():
    unapproved_profiles = Profile.objects.filter(flag=False)
    profile_list = []
    #convert from 'QuerySet' to normal Python list
    for p in unapproved_profiles:
        profile_list.append(p)
    return profile_list


def getUnapprovedInternalProfiles():
    unapproved_profiles = Profile.objects.filter(flag=False)
    profile_list = []
    for p in unapproved_profiles:
        if p.privilege_id.user_type in ["Tier_1","Tier_2"]:
            profile_list.append(p)
    return profile_list


def get_unapproved_updates():
    pending_updates = PendingProfileUpdate.objects.filter(flag=False)
    updates_list = []
    for prof_update in pending_updates:
        updates_list.append(prof_update)

    return updates_list

def get_open_account_requests():
    open_accs = Account.objects.filter(flag=False)
    accs_list = []
    for acc_update in open_accs:
        accs_list.append(acc_update)

    return accs_list

def get_close_account_requests():
    close_accs = Account.objects.filter(to_delete=True)
    close_accs_list = []
    for acc_update in close_accs:
        close_accs_list.append(acc_update)

    return close_accs_list

def getCriticalTransactions():
    #TO BE IMPLEMENTED
    return []

def _viewRequests(request):
    '''
    check logged in
    check user type
    determine type of requests to be shown
    get requests from db
    create context variable
    render page
    '''
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    
    context = {}

    if request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_1 or request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_2:
        profile_list = getUnapprovedProfiles()
        context['unapproved_profiles'] = profile_list
        '''
    elif request.user.profile.user_type == settings.SB_USER_TYPE_TIER_2:
        critical_transactions = getCriticalTransactions()
        context['critical_transactions'] = critical_transactions
        '''
    else:
        return HttpResponse("<h1>Error: 403 Forbidden</h1>")

    return render(request, 'pendingTransactions.html', context)



def _viewInternalRequests(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    
    context = {}

    if request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_3:
        profile_list = getUnapprovedInternalProfiles()
        context['unapproved_internal_profiles'] = profile_list

    else:
        return HttpResponse("<h1>Error: 403 Forbidden</h1>")

    return render(request, 'pendingTransactions.html', context)



def _view_updates(request):
    context = {}
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_1 or request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_2:
        updates_list = get_unapproved_updates()
        context['unapproved_updates'] = updates_list

    else:
        return HttpResponse("<h1>Error: 403 Forbidden</h1>")

    return render(request, 'pendingTransactions.html', context)


def _view_open_accs(request):
    context = {}
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_1 or request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_2:
        accs_list = get_open_account_requests()
        context['open_accs'] = accs_list

    else:
        return HttpResponse("<h1>Error: 403 Forbidden</h1>")

    return render(request, 'pendingTransactions.html', context)



def _view_close_accs(request):
    context = {}
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_1 or request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_2:
        accs_list = get_close_account_requests()
        context['close_accs'] = accs_list

    else:
        return HttpResponse("<h1>Error: 403 Forbidden</h1>")

    return render(request, 'pendingTransactions.html', context)


def handleUserRegistrationApproval(request):
    
    if not request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_1 or request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_2:
        return HttpResponse("<h1>Error: 403 Forbidden</h1>")

    try:
        requested_username = request.POST['requestId']
        requested_action = request.POST['status']

        requested_user = User.objects.get(username=requested_username)
        requested_profile = Profile.objects.get(user=requested_user, flag=False)

        if requested_action == "approve":
            #approve profile and default bank account

            bank_acct = Account.objects.get(user=requested_user)
            requested_profile.flag=True
            bank_acct.flag = True
            requested_profile.save()
            bank_acct.save()

        elif requested_action == "reject":
            requested_user.delete()

        return HttpResponse("200")

    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse("404")
    except KeyError:
        return HttpResponse("400")




def handleInternalUserRegistrationApproval(request):

    if not request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_3:
        return HttpResponse("<h1>Error: 403 Forbidden</h1>")

    try:

        requested_username = request.POST['requestId']
        requested_action = request.POST['status']

        requested_user = User.objects.get(username=requested_username)
        requested_profile = Profile.objects.get(user=requested_user, flag=False)

        if requested_action == "approve":
            requested_profile.flag=True
            requested_profile.save()

        elif requested_action == "reject":
            requested_user.delete()

        return HttpResponse("200")

    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse("404")
    except KeyError:
        return HttpResponse("400")





def handleOpenBankAccountApproval(request):
    
    if not request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_1 or request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_2:
        return HttpResponse("<h1>Error: 403 Forbidden</h1>")

    try:
        requested_username = request.POST['requestId']
        requested_action = request.POST['status']
        requested_acc_num = request.POST['account_number']

        requested_user = User.objects.get(username=requested_username)
        if requested_action == "approve":
            bank_acct = Account.objects.get(user=requested_user,account_number=requested_acc_num)
            bank_acct.flag = True
            bank_acct.save()

        elif requested_action == "reject":
            requested_user.delete()

        return HttpResponse("200")

    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse("404")
    except KeyError:
        return HttpResponse("400")


def handleCloseBankAccountApproval(request):
    
    if not request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_1 or request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_2:
        return HttpResponse("<h1>Error: 403 Forbidden</h1>")

    try:
        requested_username = request.POST['requestId']
        requested_action = request.POST['status']
        requested_acc_num = request.POST['account_number']

        requested_user = User.objects.get(username=requested_username)
        if requested_action == "approve":
            bank_acct = Account.objects.get(user=requested_user,account_number=requested_acc_num)
            bank_acct.delete()

        elif requested_action == "reject":
            requested_user.delete()

        return HttpResponse("200")

    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse("404")
    except KeyError:
        return HttpResponse("400")


def handleUpdatesApproval(request):
    
    if not request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_1 or request.user.Profile_User.privilege_id.user_type == settings.SB_USER_TYPE_TIER_2:
        return HttpResponse("<h1>Error: 403 Forbidden</h1>")

    try:
        requested_username = request.POST['requestId']
        requested_action = request.POST['status']
        requested_user = User.objects.get(username=requested_username)
        pending_updates = PendingProfileUpdate.objects.get(user=requested_user)
        pending_profile = Profile.objects.get(user=requested_user)
        if requested_action == "approve":

            pending_profile.street_address = pending_updates.street_address
            pending_profile.city = pending_updates.city
            pending_profile.state = pending_updates.state
            pending_profile.zip_code = pending_updates.zip_code
            pending_profile.save()
            pending_updates.delete()

        elif requested_action == "reject":
            pending_updates.delete()

        return HttpResponse("200")

    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return HttpResponse("404")
    except KeyError:
        return HttpResponse("400")

def _updateRequest(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if not request.method == 'POST':
        return HttpResponse("<h1>Error: 400 Bad Request</h1>")
    try:

        if request.POST['requestType'] == 'user_registration': #user regsitration approval
            return handleUserRegistrationApproval(request)

        else:
            return HttpResponse("<h1>Error: 400 Bad Request</h1>")

    except KeyError:
        return HttpResponse("<h1>Error: 400 Bad Request</h1>")


def _updateInternalRequest(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if not request.method == 'POST':
        return HttpResponse("<h1>Error: 400 Bad Request</h1>")
    try:

        if request.POST['requestType'] == 'internal_user_registration': #user regsitration approval
            return handleInternalUserRegistrationApproval(request)

        else:
            return HttpResponse("<h1>Error: 400 Bad Request</h1>")

    except KeyError:
        return HttpResponse("<h1>Error: 400 Bad Request</h1>")


def _approve_update(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if not request.method == 'POST':
        return HttpResponse("<h1>Error: 400 Bad Request</h1>")
    try:

        if request.POST['requestType'] == 'updates_approval':
            return handleUpdatesApproval(request)

        else:
            return HttpResponse("<h1>Error: 400 Bad Request</h1>")

    except KeyError:
        return HttpResponse("<h1>Error: 400 Bad Request</h1>")


def _approve_open_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if not request.method == 'POST':
        return HttpResponse("<h1>Error: 400 Bad Request</h1>")
    try:

        if request.POST['requestType'] == 'open_accs':
            return handleOpenBankAccountApproval(request)

        else:
            return HttpResponse("<h1>Error: 400 Bad Request</h1>")

    except KeyError:
        return HttpResponse("<h1>Error: 400 Bad Request</h1>")

def _approve_close_request(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if not request.method == 'POST':
        return HttpResponse("<h1>Error: 400 Bad Request</h1>")
    try:

        if request.POST['requestType'] == 'close_accs':
            return handleCloseBankAccountApproval(request)

        else:
            return HttpResponse("<h1>Error: 400 Bad Request</h1>")

    except KeyError:
        return HttpResponse("<h1>Error: 400 Bad Request</h1>")
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .forms import FundDepositForm, IssueChequeForm, CustomerForm
from django.conf import settings
from internal_user.approvals import _viewRequests, _updateRequest, _view_updates, _approve_update, _view_open_accs,_approve_open_request,_view_close_accs,_approve_close_request,_viewInternalRequests,_updateInternalRequest
from internal_user.utils import render_to_pdf,verify_file
from home import models
from django.contrib.auth.models import User
from home.models import Account, Cheques
from transactions.models import Transaction
import requests

def getBaseHtml(request):
    try:
        profile_instance = models.Profile.objects.get(user=request.user)
        if profile_instance.privilege_id.user_type == settings.SB_USER_TYPE_CUSTOMER:
            basehtml = "customer_homepage.html"
        elif profile_instance.privilege_id.user_type == settings.SB_USER_TYPE_TIER_1:
            basehtml = "tier1_homepage.html"
        elif profile_instance.privilege_id.user_type == settings.SB_USER_TYPE_TIER_2:
            basehtml = "tier2_homepage.html"
        else:
            basehtml = "base.html"
    except:
        basehtml = "base.html"

def initIssueCheque(request):
    context = {'context_page' : 'issue_cheque'}
    return render(request, 'init_issue_cheque.html', context)

def issueChequeTemplate(request):
    form = IssueChequeForm(initial={'customerName': request.POST['customerName'],
                                    'customerId': request.POST['customerId'],
                                    'accountId': request.POST['accountId'],
                                    'accountType': request.POST['accountType']
    })
    return render(request, 'issueCheque.html', {'form':form})

def issueCheque(request):
    if request.method == 'POST':
        form = IssueChequeForm(request.POST)
        if form.is_valid():
            account_object = Account.objects.get(account_number=form.cleaned_data.get('accountId'))
            chequeAmount = form.cleaned_data.get('chequeAmount')
            if account_object.account_balance > chequeAmount:
                ## backend code goes here
                cheque = Cheque(recipient=form.cleaned_data.get('recipientName'), amount=form.cleaned_data.get('chequeAmount'))
                messages.success(request, f'Cheque Issued successfully {cheque.id}')
                cheque_id = cheque.id
                data = {
                    'pay_to':form.cleaned_data.get('recipientName'),
                    'cheque_id': cheque_id,
                    'amount': form.cleaned_data.get('chequeAmount'),
                }
                transaction_id = Transaction.objects.get(field_type='Counter')
                url = 'http://localhost:8080/api/addTransaction'
                payload = '{"transactionId": "'+ str(transaction_id.transaction_id) +'","from": "' + str(form.cleaned_data.get('accountId')) + '", "to": "' + str('bank') + '", "amount":"' + str(form.cleaned_data.get('chequeAmount')) + '", "transactionType":"Cheque"}'
                headers = {'content-type': 'application/json',}
                r = requests.post(url, data=payload, headers=headers)
                pdf = render_to_pdf('pdf_template.html', data)
                cheque.save()
                transaction_id.transaction_id += 1
                transaction_id.save()
                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    filename = "Cheque_"+str(cheque_id)+".pdf"
                    content = "attachment; filename=%s" % (filename)
                    response['Content-Disposition'] = content
                    return response
            else:
                return render(request, 'failed.html', {'failure': '500 Error: Account not found.'}, status=500)
        else:
            messages.error(request, f'Please enter valid data')
            return redirect(settings.BASE_URL + '/internal_user/initIssueCheque')

def verifyCheque(request):
    try:
        try:
            chequeId = request.FILES['cheque'].name.split('_')[-1].replace(settings.SIGNATURE_FILES_FORMAT,'')
        except:
            return HttpResponse("Invalid file name format, file name should be of form Cheque_CHEQUEID.pdf")
        status = verify_file('public.pem', request.FILES['cheque'], settings.SIGNATURE_FILES + str(chequeId) + settings.SIGNATURE_FILES_FORMAT)
        status = not status
        context = {'tampared': status, 'basehtml': getBaseHtml(request)}
    except:
        return HttpResponse("Error occured while verifying cheque")
    return render(request, 'verify_cheque.html', context)

def initVerifyCheque(request):
    return render(request, 'init_verify.html', {'basehtml': getBaseHtml(request)})

def searchCustomer(request):
    customers = []
    user_instance = None
    try:
        user_instance = User.objects.get(username=request.POST['customerSearchString'])

        if user_instance:
            #profile = models.Profile.objects.get(user=user_instance)
            accounts = models.Account.objects.filter(user=user_instance)

            for account in accounts:
                customer = {'customerName':user_instance.first_name + ' '+user_instance.last_name,
                'customerId':user_instance.username,
                'accountId':account.account_number,
                'accountType':account.account_type}
                customers.append(customer)
        else:
            customers = []

    except:
        customers = []

    context = {
        'customers' : customers,
        'customerSearchString' : request.POST['customerSearchString']
    }
    if request.POST['context_page']=='deposit':
        return render(request, 'init_fund_deposit.html', context)
    elif request.POST['context_page']=='issue_cheque':
        return render(request, 'init_issue_cheque.html', context)
    elif request.POST['context_page']=='view_customer':
        return render(request, 'init_view_customer.html', context)
    elif request.POST['context_page']=='modify_customer':
        return render(request, 'init_modify_customer.html', context)
    elif request.POST['context_page']=='delete_customer':
        return render(request, 'delete_customer_account.html', context)

def initViewCustomer(request):
    context = {'context_page' : 'view_customer'}
    return render(request, 'init_view_customer.html', context)

def viewCustomer(request):
    if request.method == 'POST':
        user_instance = User.objects.get(username=request.POST['customerId'])
        try:
            accounts = models.Account.objects.filter(user=user_instance)
        except:
            account = []
        print(request.POST['customerId'])
        form = CustomerForm(initial={'customerName': request.POST['customerName'],
                                    'customerId': request.POST['customerId'],
                                    'accountId': request.POST['accountId'],
                                    'accountType': request.POST['accountType'],
                                    'customerEmail':user_instance.email,


        })
        ##Get all customer realted data from database and populate form

        return render(request, 'view_customer.html', {'form':form,'accounts':accounts})

def createCustomer(request):
    return redirect(settings.BASE_URL+'/create_account')

def initModifyCustomer(request):
    context = {'context_page' : 'modify_customer'}
    return render(request, 'init_modify_customer.html', context)

def viewRequests(request):
    return _viewRequests(request)

def updateRequest(request):
    return _updateRequest(request)

def viewInternalRequests(request):
    return _viewInternalRequests(request)

def view_updates(request):
    return _view_updates(request)

def view_open_accs(request):
    return _view_open_accs(request)

def view_close_accs(request):
    return _view_close_accs(request)

def updateInternalRequest(request):
    return _updateInternalRequest(request)

def approve_update(request):
    return _approve_update(request)

def approve_open_request(request):
    return _approve_open_request(request)

def approve_close_request(request):
    return _approve_close_request(request)
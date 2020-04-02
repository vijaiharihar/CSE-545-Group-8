from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .forms import FundTransferForm
from django.conf import settings
from django.http import FileResponse

import base64
import requests
import json
from fpdf import FPDF
from datetime import date, datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
import cryptography.exceptions
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import rsa
from transactions.models import Pending_Transactions, Transaction
from home.models import Account
from transactions.forms import FundDepositWithdrawForm
import mimetypes


def fundTransfer(request):
    if request.method == 'POST':
        form = FundTransferForm(request.POST)
        if form.is_valid():
            transferAmount = form.cleaned_data.get('transferAmount')
            from_account = form.cleaned_data.get('fromAccount')
            to_account = form.cleaned_data.get('toAccount')
            account = Account.objects.get(account_number=from_account)
            if account.account_balance > transferAmount:
                today = date.today()
                url = 'http://localhost:8080/api/query'
                payload = '{"from": "' + str(from_account) + '", "date":"' + today.strftime("%m/%d/%Y") + '"}'
                headers = {'content-type': 'application/json', }
                r = requests.get(url, data=payload, headers=headers)
                json_data = json.loads(r.json()['response'])
                daily_transaction = 0
                for val in json_data:
                    daily_transaction += float(val['Record']['amount'])
                transaction_id = Transaction.objects.get(field_type='Counter')
                print(daily_transaction)
                if daily_transaction <= 1000 and transferAmount <= 1000:
                    url = 'http://localhost:8080/api/addTransaction'
                    payload = '{"transactionId": "' + str(transaction_id.transaction_id) + '","from": "' + str(
                        from_account) + '", "to": "' + str(to_account) + '", "amount":"' + str(
                        transferAmount) + '", "transactionType":"Debit"}'
                    headers = {'content-type': 'application/json', }
                    r = requests.post(url, data=payload, headers=headers)
                    account = Account.objects.get(account_number=from_account)
                    account.account_balance -= float(transferAmount)
                    account.save()
                    account = Account.objects.get(account_number=to_account)
                    account.account_balance += float(transferAmount)
                    account.save()
                    messages.success(request, f'Fund transfered successfully {transferAmount}')
                else:
                    pending = Pending_Transactions()
                    pending.transaction_id = transaction_id.transaction_id
                    pending.from_account = from_account
                    pending.to_account = to_account
                    pending.transaction_value = transferAmount
                    pending.transaction_date = datetime.now()
                    pending.transaction_type = 'Critical'
                    pending.save()
                    messages.success(request, f'Fund transfer in review {transferAmount}')
                transaction_id.transaction_id += 1
                transaction_id.save()
                return redirect(settings.BASE_URL + '/user_home')
            else:
                messages.error(request, f'Form is not valid')
                return redirect(settings.BASE_URL + '/user_home')
        else:
            return render(request, 'failed.html', {'failure': '403 Error: Account balance too small.'},
                          status=403)
    else:
        return render(request, 'fundTransfer.html')


def fund_deposit(request):
    """Deposits the given amount of money into the specified bank account"""
    if request.method == 'POST':
        form = FundDepositWithdrawForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data.get('accountId')
            amount = form.cleaned_data.get('amount')
            account_object = Account.objects.get(account_number=account)

            # Check that account was found
            if account_object is not None:
                if account_object.account_type == 'credit_card':
                    if account_object.account_balance + amount > 2000:
                        messages.success(request, f'Cannot pay over limit of $2000.')
                        return render(request, 'failed.html', {'failure': 'Cannot pay over limit of $2000.'}, status=500)
                    else:
                        transaction_id = Transaction.objects.get(field_type='Counter')
                        pending = Pending_Transactions()
                        pending.transaction_id = transaction_id.transaction_id
                        pending.from_account = 'self'
                        pending.to_account = account
                        pending.transaction_value = amount
                        pending.transaction_date = datetime.now()
                        pending.transaction_type = 'Deposit'
                        pending.save()
                        transaction_id.transaction_id += 1
                        transaction_id.save()
                        messages.success(request, f'Transaction transfer in review {amount}')
                else:
                    transaction_id = Transaction.objects.get(field_type='Counter')
                    pending = Pending_Transactions()
                    pending.transaction_id = transaction_id.transaction_id
                    pending.from_account = 'self'
                    pending.to_account = account
                    pending.transaction_value = amount
                    pending.transaction_date = datetime.now()
                    pending.transaction_type = 'Deposit'
                    pending.save()
                    transaction_id.transaction_id += 1
                    transaction_id.save()
                    messages.success(request, f'Transaction transfer in review {amount}')
                return render(request, 'success.html')
            else:
                return render(request, 'failed.html', {'failure': '500 Error: Account not found.'}, status=500)
        else:
            return render(request, 'failed.html', {'failure': '405 Error: Incorrect input.'}, status=405)
    elif request.method == 'GET':
        accounts_list = Account.objects.filter(user=request.user)
        accounts = []
        for account in accounts_list:
            accounts.append({"number": account.account_number, "type": account.account_type})
        return render(request, 'deposit.html', {"accounts": accounts})
    else:
        return render(request, 'failed.html', {'failure': '405 Error: Method not supported.'}, status=405)


def fund_withdraw(request):
    """Withdraws the given amount of money from the specified bank account"""
    if request.method == 'POST':
        form = FundDepositWithdrawForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data.get('accountId')
            amount = form.cleaned_data.get('amount')
            account_object = Account.objects.get(account_number=account)

            # Check that account was found
            if account_object is not None:
                # Check for adequate funds
                if account_object.account_balance >= amount:
                    transaction_id = Transaction.objects.get(field_type='Counter')
                    pending = Pending_Transactions()
                    pending.transaction_id = transaction_id.transaction_id
                    pending.from_account = account
                    pending.to_account = 'self'
                    pending.transaction_value = amount
                    pending.transaction_date = datetime.now()
                    pending.transaction_type = 'Withdraw'
                    pending.save()
                    transaction_id.transaction_id += 1
                    transaction_id.save()
                    messages.success(request, f'Transaction transfer in review {amount}')
                    return render(request, 'success.html')
                else:
                    return render(request, 'failed.html', {'failure': '403 Error: Account balance too small.'},
                                  status=403)
            else:
                return render(request, 'failed.html', {'failure': '500 Error: Account not found.'}, status=500)
        else:
            return render(request, 'failed.html', {'failure': '400 Error: Bad request.'}, status=400)
    elif request.method == 'GET':
        accounts_list = Account.objects.filter(user=request.user)
        accounts = []
        for account in accounts_list:
            accounts.append({"number": account.account_number, "type": account.account_type})
        return render(request, 'withdraw.html', {"accounts": accounts})
    else:
        return render(request, 'failed.html', {'failure': '405 Error: Method not supported.'}, status=405)


def initfundTransfer(request):
    return render(request, 'fundTransfer.html')


def pendingTrans(request):
    pending = Pending_Transactions.objects.all()
    context = {
        'pending': pending
    }
    return render(request, 'pendingTransactions.html', context)


def updateTransaction(request):
    if request.method == 'POST':
        if request.POST['status'] == 'approve':
            transactionId = request.POST['transactionId']
            pending = Pending_Transactions.objects.get(transaction_id=int(transactionId))
            if pending.from_account != 'self' and pending.to_account != 'self':
                account = Account.objects.get(account_number=pending.from_account)
                account.account_balance -= float(pending.transaction_value)
                account.save()
                account = Account.objects.get(account_number=pending.to_account)
                account.account_balance += float(pending.transaction_value)
                account.save()
            elif pending.from_account != 'self':
                account = Account.objects.get(account_number=pending.from_account)
                if pending.transaction_type == 'Withdraw' and account.account_balance > pending.transferAmount:
                    account.account_balance -= float(pending.transaction_value)
                    account.save()
                else:
                    return render(request, 'failed.html', {'failure': '403 Error: Account balance too small.'},
                                  status=403)
            elif pending.from_account == 'self':
                account = Account.objects.get(account_number=pending.to_account)
                account.account_balance += float(pending.transaction_value)
                account.save()
            url = 'http://localhost:8080/api/addTransaction'
            payload = '{"transactionId": "' + str(pending.transaction_id) + '","from": "' + str(
                pending.from_account) + '", "to": "' + str(pending.to_account) + '", "amount":"' + str(
                pending.transaction_value) + '", "transactionType":"Deposit"}'
            headers = {'content-type': 'application/json', }
            r = requests.post(url, data=payload, headers=headers)
            pending.delete()
    return HttpResponse({'value': 'success'}, status=200)


def generateStatements(request):
    if request.method == 'POST':
        account_number = request.POST['accountId']
        account_object = Account.objects.get(account_number=account_number)
        if account_object is not None:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            row_height = pdf.font_size
            spacing = 4
            pdf.write(row_height, 'Account Number: {}\n'.format(account_object.account_number))
            pdf.write(row_height, 'Account Type: {}\n'.format(account_object.account_type))
            pdf.write(row_height, 'Account Balance: {}\n\n'.format(account_object.account_balance))
            col_width = pdf.w / 4.5
            records = [['Recipient', 'Amount', 'Date', 'Time']]
            url = 'http://localhost:8080/api/query'
            payload = '{"from": "' + str(account_object.account_number) + '"}'
            headers = {'content-type': 'application/json', }
            r = requests.get(url, data=payload, headers=headers)
            json_data = json.loads(r.json()['response'])
            row_data = []
            for row in json_data:
                row_data.append(row['Record']['from'])
                row_data.append(row['Record']['amount'])
                row_data.append(row['Record']['date'])
                row_data.append(row['Record']['time'])
                records.append(row_data)
            for row in records:
                for item in row:
                    pdf.cell(col_width, row_height * spacing,
                             txt=item, border=1)
                pdf.ln(row_height * spacing)
            filename = '{}-{}.pdf'.format(account_object.account_number, datetime.now())
            pdf.output('./transactions/statements/' + filename)
            # fill these variables with real values
            with open('./transactions/statements/' + filename, 'rb') as pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = "attachment; filename=%s" % filename
                return response
        else:
            return render(request, 'failed.html', {'failure': '500 Error: Account not found.'}, status=500)
    elif request.method == 'GET':
        accounts_list = Account.objects.filter(user=request.user)
        accounts = []
        for account in accounts_list:
            accounts.append({"number": account.account_number, "type": account.account_type})
        return render(request, 'statements.html', {"accounts": accounts})


# generate key function
# generate private key and public key
def generate_key():
    # Generate the public/private key pair.
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend(),
    )

    # Save the private key to a file.
    with open('private.key', 'wb') as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    # Save the public key to a file.
    with open('public.pem', 'wb') as f:
        f.write(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
    return


# sign file function
# use private key to sign statement file
# generate sign file, it use to verificate
# The sign file and statement file is corresponding
# private_key---string of private_key file
# file_name ---- string of file should sign
def sign_file(private_key, file_name):
    # Load the private key.
    # private_key=private.key
    with open(private_key, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend(),
        )
    # Load the contents of the file to be signed.
    # file_name='statement.txt'
    with open(file_name, 'rb') as f:
        payload = f.read()

    # Sign the payload file.
    # genertae sign file, it should send to verification
    signature = base64.b64encode(
        private_key.sign(
            payload,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    )
    with open('signature.sig', 'wb') as f:
        f.write(signature)
    return


# verificate_file function
# need statement file and sign file,  two file is corresponding
# public_key---string of private_key file
# file_name ---- string of file should verificate
# sign_file ----- string of sign file which generate by sign file function, use to verificate
def verificate_file(public_key, file_name, sign_file):
    # Load the public key.
    # public_key=public.pem
    with open(public_key, 'rb') as f:
        public_key = load_pem_public_key(f.read(), default_backend())

    # Load the statement contents and the signature.
    # file_name='statement.txt'
    with open(file_name, 'rb') as f:
        payload_contents = f.read()
    # sign_file='signature.sig'
    with open(sign_file, 'rb') as f:
        signature = base64.b64decode(f.read())

    # Perform the verification.
    try:
        public_key.verify(
            signature,
            payload_contents,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        # this file is pass verification
        # to do more
        ##############
    except cryptography.exceptions.InvalidSignature as e:
        # this file is fail
        # ERROR
        print('ERROR: Payload and/or signature files failed verification!')
    return

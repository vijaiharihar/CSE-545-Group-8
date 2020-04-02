from django import forms
from django.core.validators import MinValueValidator

class FundDepositForm(forms.Form):
    customerName = forms.CharField(label='Name')
    customerId = forms.CharField(label='Customer Id', validators=[MinValueValidator(1)])
    accountId = forms.IntegerField(label='Account Id', validators=[MinValueValidator(1)])
    accountType = forms.CharField(label='Account type')
    depositAmount = forms.FloatField(label='Deposit amount', validators=[MinValueValidator(0.01)])

class IssueChequeForm(forms.Form):
    customerName = forms.CharField(label='Name')
    accountId = forms.IntegerField(label='Account Id', validators=[MinValueValidator(1)])
    accountType = forms.CharField(label='Account type')
    chequeAmount = forms.FloatField(label='Cheque amount', validators=[MinValueValidator(0.01)])
    recipientName = forms.CharField(label='Recipient name')

class CustomerForm(forms.Form):
    customerName = forms.CharField(label='Name')
    customerId = forms.CharField(label='Customer Id')
    accountId = forms.IntegerField(label='Account Id', validators=[MinValueValidator(1)])
    accountType = forms.CharField(label='Account type')
    customerEmail = forms.EmailField(label='Email')

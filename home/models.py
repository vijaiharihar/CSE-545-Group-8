from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from uuid import uuid4
from random import randint



class Privilege(models.Model):
    view_transaction = models.BooleanField()
    create_transaction = models.BooleanField()
    authorize_transaction = models.BooleanField()
    transaction_type = models.CharField(max_length=20)
    issue_check = models.BooleanField()
    fund_transfer = models.BooleanField()
    view_account = models.BooleanField()
    create_account = models.BooleanField()
    modify_account = models.BooleanField()
    close_account = models.BooleanField()
    delete_account = models.BooleanField()
    access_logs = models.BooleanField()
    user_type = models.CharField(max_length=10)

    def __str__(self):
        return self.user_type

class PendingProfileUpdate(models.Model):
    first_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=20)
    street_address = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip_code = models.IntegerField()
    mobile_number = models.CharField(max_length=10,unique=True)
    username = models.CharField(max_length=20,unique=True)

    def __str__(self):
            return self.username

class Profile(models.Model):
    user = models.OneToOneField(User,related_name="Profile_User", on_delete=models.CASCADE)
    street_address = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip_code = models.IntegerField()
    mobile_number = models.CharField(max_length=10,unique=True)
    birthdate = models.DateTimeField()
    ssn = models.CharField(max_length=9,unique=True)
    joining_date = models.DateTimeField(default=datetime.now)
    flag = models.BooleanField(default=False)
    privilege_id=models.ForeignKey(Privilege,related_name='ProfilePrivilege',on_delete=models.CASCADE,default='')
    
    def __str__(self):
        if self.user:
            return self.user.username

class Account(models.Model):
    ACCOUNT_TYPE = (
    ('savings','SAVINGS'),
    ('checking', 'CHECKING'),
    ('credit_card','CREDIT_CARD'),
    )
    account_number=models.AutoField(primary_key=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE)
    account_balance = models.FloatField(default=0)
    creation_date = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(User,related_name="Account_User_id", on_delete=models.CASCADE)
    flag = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)

    def __int__(self):
        return self.account_number

class Transaction(models.Model):
    from_account = models.IntegerField()
    to_account = models.IntegerField()
    transaction_value = models.BigIntegerField()
    transaction_date = models.DateTimeField()
    transaction_type = models.CharField(max_length=20)
    transaction_status = models.CharField(max_length=20)
    user = models.ForeignKey(User, related_name="Transaction_User_id", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Appointment(models.Model):
    ASSIGNED_TYPE = (
    ('TIER1','TIER1'),
    ('TIER2', 'TIER2'),
    ('TIER3','TIER3'),
    )
    appointment_date = models.DateTimeField()
    appointment_subject = models.TextField()
    appointment_assigned_to = models.CharField(max_length=20,choices=ASSIGNED_TYPE)
    user = models.ForeignKey(User, related_name="Appointment_User", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Requests(models.Model):
    request_date = models.DateTimeField()
    request_subject = models.TextField()
    request_assigned_to = models.IntegerField()
    request_type = models.CharField(max_length=20)
    user = models.ForeignKey(User,related_name="Requests_User_id", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

  #it is for login history  
class AllLogin(models.Model):
    user = models.ForeignKey(User,related_name="Requests_User_id", on_delete=models.CASCADE)
    date= models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return str(self.user) + ': ' + str(self.date)

from django.db import models


# Create your models here.
class Transaction(models.Model):
    transaction_id = models.IntegerField(default=0)
    field_type = models.CharField(default='Counter', max_length=10)


class Pending_Transactions(models.Model):
    from_account = models.CharField(max_length=20)
    to_account = models.CharField(max_length=20)
    transaction_value = models.DecimalField(max_digits=7, decimal_places=2)
    transaction_date = models.DateTimeField()
    transaction_type = models.CharField(max_length=20)
    transaction_id = models.IntegerField()

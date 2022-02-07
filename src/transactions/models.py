from django.db import models


class Transaction(models.Model):
    account_no = models.CharField(max_length=64)
    amount = models.PositiveIntegerField()
    created_datetime = models.DateTimeField()

class Balance(models.Model):
    account_no = models.CharField(max_length=64, unique=True)
    balance = models.PositiveIntegerField(default=0)
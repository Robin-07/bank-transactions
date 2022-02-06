from django.db import models


class Transaction(models.Model):
    account_no = models.CharField(max_length=64, unique=True)
    amount = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)

class Balance(models.Model):
    account_no = models.CharField(max_length=64, unique=True)
    balance = models.PositiveIntegerField(default=0)
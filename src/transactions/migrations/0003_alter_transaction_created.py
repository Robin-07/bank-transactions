# Generated by Django 4.0.2 on 2022-02-07 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_alter_balance_balance_alter_transaction_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='created',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
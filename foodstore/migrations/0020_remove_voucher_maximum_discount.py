# Generated by Django 3.0.8 on 2020-12-26 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodstore', '0019_customer_used_vouchers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voucher',
            name='maximum_discount',
        ),
    ]

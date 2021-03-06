# Generated by Django 3.0.8 on 2020-12-17 17:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodstore', '0012_auto_20201218_0057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='deliveryInfo',
        ),
        migrations.AddField(
            model_name='deliveryinfo',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='foodstore.Customer'),
        ),
        migrations.AddField(
            model_name='deliveryinfo',
            name='default',
            field=models.BooleanField(default=True),
        ),
    ]

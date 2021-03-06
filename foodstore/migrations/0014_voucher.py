# Generated by Django 3.0.8 on 2020-12-26 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodstore', '0013_auto_20201218_0127'),
    ]

    operations = [
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, null=True)),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField()),
                ('min_purchase', models.FloatField()),
                ('discount_unit', models.CharField(choices=[('RM', 'RM'), ('%', '%')], default='RM', max_length=2)),
                ('discount', models.IntegerField()),
                ('maximum_discount', models.IntegerField(blank=True, null=True)),
                ('active', models.BooleanField()),
            ],
        ),
    ]

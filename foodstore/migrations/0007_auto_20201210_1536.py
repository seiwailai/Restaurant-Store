# Generated by Django 3.0.8 on 2020-12-10 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodstore', '0006_category_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ManyToManyField(to='foodstore.Category'),
        ),
    ]

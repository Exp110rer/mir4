# Generated by Django 4.1.6 on 2023-10-29 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_api', '0002_order_customerordernumber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customerOrderNumber',
            field=models.CharField(max_length=10, verbose_name='Customer Order number'),
        ),
    ]

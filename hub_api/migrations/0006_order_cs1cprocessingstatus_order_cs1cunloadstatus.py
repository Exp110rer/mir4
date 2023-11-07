# Generated by Django 4.1.6 on 2023-11-07 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_api', '0005_order_cs1creadinessstatus_order_csdownloadstatus_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cs1CProcessingStatus',
            field=models.CharField(blank=True, choices=[('OK', 'Processed'), ('NOK', 'Error processing')], default=None, max_length=3, null=True, verbose_name='Customer Service 1C processing status '),
        ),
        migrations.AddField(
            model_name='order',
            name='cs1CUnloadStatus',
            field=models.BooleanField(default=False, verbose_name='Customer Service 1C unloading status '),
        ),
    ]

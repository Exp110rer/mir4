# Generated by Django 4.1.5 on 2023-03-24 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='item',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='order',
            name='traceability',
            field=models.BooleanField(default=True, verbose_name='Traceability identification'),
        ),
    ]

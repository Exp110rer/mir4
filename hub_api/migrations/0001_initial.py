# Generated by Django 4.1.5 on 2023-03-23 19:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mirusers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Update date')),
                ('order', models.CharField(db_index=True, max_length=10, verbose_name='Order number')),
                ('saleType', models.CharField(choices=[('RU12', 'SPB_to_ITMS'), ('RU14', 'ITMS_to_SNS')], max_length=4, verbose_name='Sale operation type')),
                ('contractType', models.CharField(choices=[('t', 'Traditional'), ('c', 'Consignment')], max_length=1, verbose_name='Contract type')),
                ('buyoutDate', models.DateField(verbose_name='Date of planned buyout')),
                ('validation_uuid', models.UUIDField(blank=True, null=True, verbose_name='Validation uuid')),
                ('itemsCount', models.PositiveSmallIntegerField(default=0, verbose_name='Quantity of items')),
                ('partial', models.BooleanField(default=False, verbose_name='Integrity status')),
                ('iteration', models.SmallIntegerField(default=1, verbose_name='Order processing iteration number')),
                ('status', models.SmallIntegerField(default=0, verbose_name='Order status')),
                ('hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mirusers.hub', verbose_name='Shipped from location')),
                ('updatedBy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updatedBy', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
                'unique_together': {('order', 'saleType')},
            },
        ),
        migrations.CreateModel(
            name='Composition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Update date')),
                ('sku', models.PositiveIntegerField(verbose_name='SKU number')),
                ('amount', models.PositiveIntegerField(verbose_name='Number of case')),
                ('unitOfMeasure', models.CharField(choices=[('case', 'mastercase'), ('out', 'outer')], max_length=10, verbose_name='Item Unit of measure')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sPositionSet', to='hub_api.order')),
            ],
            options={
                'verbose_name': 'Order composition',
                'verbose_name_plural': 'Order compositions',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Update date')),
                ('uid', models.CharField(max_length=70, verbose_name='Item uniques id')),
                ('tuid', models.CharField(db_index=True, max_length=70, verbose_name='Tracking code')),
                ('validity', models.SmallIntegerField(default=0, verbose_name='Item verification status')),
                ('unitOfMeasure', models.CharField(choices=[('case', 'mastercase'), ('out', 'outer')], max_length=10, verbose_name='Item Unit of measure')),
                ('sku', models.PositiveIntegerField(verbose_name='SKU number')),
                ('batch', models.CharField(blank=True, max_length=10, null=True, verbose_name='Batch number')),
                ('iteration', models.SmallIntegerField(default=1, verbose_name='Item processing iteration number')),
                ('composition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sUSNSet', to='hub_api.composition')),
            ],
            options={
                'verbose_name': 'Item',
                'verbose_name_plural': 'Items',
                'unique_together': {('uid', 'composition')},
            },
        ),
    ]

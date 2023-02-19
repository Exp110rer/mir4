from django.db import models
from django.contrib.auth import get_user_model
from mirusers.models import Hub


class DateTimeModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    updated = models.DateTimeField(auto_now=True, verbose_name='Update date')

    class Meta:
        abstract = True


class Order(DateTimeModel):
    OPERATION_TYPE_CHOICES = [
        ('RU12', 'SPB_to_ITMS'),
        ('RU14', 'ITMS_to_SNS')
    ]

    CONTRACT_TYPE_CHOICES= [
        ('t', 'Traditional'),
        ('c', 'Consignment')
    ]
    order = models.CharField(max_length=10, verbose_name='Order number', db_index=True)
    shipFrom = models.ForeignKey(Hub, on_delete=models.CASCADE, verbose_name='Shipped from location')
    operationType = models.CharField(max_length=4, verbose_name='Sale operation type', choices=OPERATION_TYPE_CHOICES)
    contractType = models.CharField(max_length = 1, verbose_name='Contract type', choices=CONTRACT_TYPE_CHOICES)
    itemsCount = models.PositiveSmallIntegerField(verbose_name='Quantity of items')
    partial = models.BooleanField(verbose_name='Integrity status')
    iteration = models.SmallIntegerField(default=1, verbose_name='Order processing iteration number')
    status = models.SmallIntegerField(default=0, verbose_name='Order status')
    updatedBy = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Updated by',
                                  related_name='updatedBy')

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class Item(DateTimeModel):
    UOM_CHOICES = [('case', 'mastercase'), ('out', 'outer')]
    uid = models.CharField(max_length=70, verbose_name='Item uniques id, T&T code', db_index=True)
    validity = models.SmallIntegerField(default=0, verbose_name='Item verification status')
    uom = models.CharField(max_length=10, verbose_name='Item Unit of measure', choices=UOM_CHOICES)
    sku = models.PositiveIntegerField(verbose_name='SKU number')
    batch = models.CharField(max_length=10, verbose_name='Batch number', null=True, blank=True)
    iteration = models.SmallIntegerField(default=1, verbose_name='Item processing iteration number')
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.uid}"

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

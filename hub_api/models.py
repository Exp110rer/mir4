from django.db import models
from django.contrib.auth import get_user_model
from mirusers.models import Hub

UOM_CHOICES = [('case', 'mastercase'), ('out', 'outer')]
OPERATION_TYPE_CHOICES = [('RU12', 'SPB_to_ITMS'), ('RU14', 'ITMS_to_SNS')]
CONTRACT_TYPE_CHOICES = [('t', 'Traditional'), ('c', 'Consignment')]


class DateTimeModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    updated = models.DateTimeField(auto_now=True, verbose_name='Update date')

    class Meta:
        abstract = True


class Order(DateTimeModel):
    order = models.CharField(max_length=10, verbose_name='Order number', db_index=True)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, verbose_name='Shipped from location')
    saleType = models.CharField(max_length=4, verbose_name='Sale operation type', choices=OPERATION_TYPE_CHOICES)
    contractType = models.CharField(max_length=1, verbose_name='Contract type', choices=CONTRACT_TYPE_CHOICES)
    itemsCount = models.PositiveSmallIntegerField(default=0, verbose_name='Quantity of items')
    partial = models.BooleanField(default=False, verbose_name='Integrity status')
    iteration = models.SmallIntegerField(default=1, verbose_name='Order processing iteration number')
    status = models.SmallIntegerField(default=0, verbose_name='Order status')
    updatedBy = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Updated by',
                                  related_name='updatedBy')

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        unique_together = ('order', 'saleType')


class Composition(DateTimeModel):
    sku = models.PositiveIntegerField(verbose_name='SKU number')
    amount = models.PositiveIntegerField(verbose_name='Number of case')
    unitOfMeasure = models.CharField(max_length=10, verbose_name='Item Unit of measure', choices=UOM_CHOICES)
    order = models.ForeignKey(Order, related_name='sPositionSet', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.order.order}"

    class Meta:
        verbose_name = 'Order composition'
        verbose_name_plural = 'Order compositions'


class Item(DateTimeModel):
    uid = models.CharField(max_length=70, verbose_name='Item uniques id, T&T code', db_index=True)
    validity = models.SmallIntegerField(default=0, verbose_name='Item verification status')
    unitOfMeasure = models.CharField(max_length=10, verbose_name='Item Unit of measure', choices=UOM_CHOICES)
    sku = models.PositiveIntegerField(verbose_name='SKU number')
    batch = models.CharField(max_length=10, verbose_name='Batch number', null=True, blank=True)
    iteration = models.SmallIntegerField(default=1, verbose_name='Item processing iteration number')
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE, related_name='sUSNSet')

    # order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.uid}"

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

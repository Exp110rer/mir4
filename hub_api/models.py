from django.db import models


class DateTimeModel(models.Model):
    created = models.DateField(auto_now_add=True, verbose_name='Creation date')
    updated = models.DateField(auto_now=True, verbose_name='Update date')

    class Meta:
        abstract = True


class Order(DateTimeModel):
    number = models.CharField(max_length=10, verbose_name='Order number')
    ship_from = models.CharField(max_length=10, verbose_name='Shipped from location')
    status = models.SmallIntegerField(default=0, verbose_name='Order status')
    iteration = models.SmallIntegerField(default=1, verbose_name='Order processing iteration number')

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class Item(DateTimeModel):
    uid = models.CharField(max_length=20, verbose_name='Item uniques id, T&T code')
    validity = models.SmallIntegerField(default=0, verbose_name='Item verification status')
    uom = models.CharField(max_length=10, default='MC', verbose_name='Item Unit of measure', db_index=True)
    iteration = models.SmallIntegerField(default=1, verbose_name='Item processing iteration number')
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.uid}"

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

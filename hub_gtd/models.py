from django.db import models
from uuid import uuid4


# Create your models here.

class DateTimeModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    updated = models.DateTimeField(auto_now=True, verbose_name='Update date')

    class Meta:
        abstract = True


class GTD(DateTimeModel):
    gtd = models.CharField(max_length=50, verbose_name='Customs declaration number')
    guid = models.UUIDField(unique=True, verbose_name='Unique GTD ids')

    def __str__(self):
        return self.gtd

    class Meta:
        verbose_name = 'GTD'
        verbose_name_plural = 'GTDs'


class SKU(DateTimeModel):
    sku = models.PositiveIntegerField(verbose_name='SKU number', db_index=True)
    gtd = models.ManyToManyField(GTD, verbose_name='Customs declaration number', related_name='items')

    class Meta:
        verbose_name = 'SKU'
        verbose_name_plural = 'SKUs'


class Item(DateTimeModel):
    tuid = models.CharField(max_length=70, verbose_name='Tracking code', db_index=True, unique=True)
    gtd = models.ForeignKey(GTD, verbose_name='Customs declaration number', on_delete=models.CASCADE)
    sku = models.ForeignKey(SKU, verbose_name='SKU number', on_delete=models.CASCADE, related_name='tuids')

    def __str__(self):
        return self.tuid

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

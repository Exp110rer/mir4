from django.db import models
from ext_tnt.apps import ExtTntConfig


class DateTimeModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = ExtTntConfig.name


class Aggregation(DateTimeModel):
    participantId = models.CharField(max_length=10)
    productionLineId = models.CharField(max_length=10)
    productionOrderId = models.CharField(max_length=20)
    sku = models.PositiveIntegerField()
    batch = models.CharField(max_length=10)
    uuid = models.UUIDField(db_index=True)
    updatedBy = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Aggregation'
        verbose_name_plural = 'Aggregations'
        app_label = ExtTntConfig.name


class Unit(DateTimeModel):
    unitSerialNumber = models.CharField(max_length=70, db_index=True)
    aggregatedItemsCount = models.PositiveSmallIntegerField()
    aggregationType = models.CharField(max_length=15, default='AGGREGATION')
    aggregationUnitCapacity = models.PositiveSmallIntegerField()
    aggregation = models.ForeignKey(Aggregation, on_delete=models.DO_NOTHING, related_name='aggregationUnits')
    uuid = models.UUIDField(db_index=True)

    class Meta:
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'
        app_label = ExtTntConfig.name


class Item(DateTimeModel):
    unitSerialNumber = models.CharField(max_length=70, db_index=True)
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING, related_name='sntins')
    aggregation = models.ForeignKey(Aggregation, on_delete=models.DO_NOTHING, related_name='items')
    uuid = models.UUIDField(db_index=True)

    def __str__(self):
        return f"{self.unitSerialNumber}"

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        app_label = ExtTntConfig.name

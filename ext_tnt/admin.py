import uuid

from django.contrib import admin
from ext_tnt.models import Item, Unit, Aggregation


# Register your models here.

@admin.register(Item)
class ItemModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Unit)
class UnitModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Aggregation)
class AggregationModelAdmin(admin.ModelAdmin):
    pass

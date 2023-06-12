from django.contrib import admin
from hub_gtd.models import Item, SKU, GTD


# Register your models here.

@admin.register(Item)
class ItemModelAdmin(admin.ModelAdmin):
    pass


@admin.register(SKU)
class SKUModelAdmin(admin.ModelAdmin):
    pass


@admin.register(GTD)
class GTDModelAdmin(admin.ModelAdmin):
    pass

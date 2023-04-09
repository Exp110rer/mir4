from django.contrib import admin
from hub_api.models import Order, Item, Composition, ProductCategory


# Register your models here.
@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Item)
class ItemModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Composition)
class SkuModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'traceability')

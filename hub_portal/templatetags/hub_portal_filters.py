from django import template
from hub_api.models import ProductCategory

register = template.Library()

product_category = ProductCategory.objects.all()


def product_category_name(value):
    return product_category.get(name=value).description


def order_sale_type(value):
    if value == 'RU12':
        return 'БАТ'
    elif value == 'RU14':
        return 'МУМТ'
    else:
        return 'неизвестно'


def order_contract_type(value):
    if value == 't':
        return 's'
    elif value == 'c':
        return 'k'
    else:
        return 'неизвестно'


register.filter('product_category_name', product_category_name)
register.filter('order_sale_type', order_sale_type)
register.filter('order_contract_type', order_contract_type)

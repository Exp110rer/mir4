from django import template
from hub_api.models import ProductCategory

register = template.Library()

product_category = ProductCategory.objects.all()


def product_category_name(value):
    # return ProductCategory.objects.get(name=value).description
    return product_category.get(name=value).description


register.filter('category_name', product_category_name)

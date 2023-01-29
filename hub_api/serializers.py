from rest_framework import serializers
from hub_api.models import Order, Item
from rest_framework.request import Request


class ItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['uid']


class OrderModelSerializer(serializers.ModelSerializer):
    items = ItemModelSerializer(many=True)

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        try:
            new_order = Order.objects.get(number=validated_data.get('number'))
        except Order.DoesNotExist:
            new_order = Order.objects.create(**validated_data)
        else:
            new_order.iteration += 1
            new_order.save(update_fields=['iteration'])
        for item_data in items_data:
            Item.objects.create(order=new_order, iteration=new_order.iteration, **item_data)
        return new_order

    class Meta:
        model = Order
        fields = '__all__'

from rest_framework import serializers
from rest_framework.request import Request
from hub_api.models import Order, Item
from mirusers.models import Hub, MirUser


class ItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['uid', 'sku', 'batch']


class OrderModelSerializer(serializers.ModelSerializer):
    items = ItemModelSerializer(many=True)
    shipFrom = serializers.CharField()

    def validate_shipFrom(self, value):
        try:
            hub = Hub.objects.get(name=value)
        except Hub.DoesNotExist:
            raise serializers.ValidationError('The specified hub does not exist.')
        else:
            if MirUser.objects.get(id=self.initial_data['updatedBy']).hub == hub or \
                    MirUser.objects.get(id=self.initial_data['updatedBy']).hub.name == 'H00B':
                return hub
            else:
                raise serializers.ValidationError('The specified hub does not match the sender.')

    def validate_itemsCount(self, value):
        try:
            status = value == len(self.initial_data['items'])
        except KeyError as error:
            raise serializers.ValidationError(f"Field {error} is required")
        else:
            if status:
                return value
            else:
                raise serializers.ValidationError("itemsCount does not match the number of items")

    # def validate_shipFrom(self, value):
    #     pass

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        try:
            new_order = Order.objects.get(order=validated_data.get('order'))
        except Order.DoesNotExist:
            new_order = Order.objects.create(**validated_data)
        else:
            new_order.iteration += 1
            new_order.partial = validated_data['partial']
            new_order.updatedBy = validated_data['updatedBy']
            new_order.save(update_fields=['iteration', 'partial', 'updatedBy', 'updated'])
        for item_data in items_data:
            Item.objects.create(order=new_order, iteration=new_order.iteration, **item_data)
        return new_order

    class Meta:
        model = Order
        fields = '__all__'

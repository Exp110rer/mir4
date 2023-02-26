from rest_framework import serializers
from hub_api.models import Order, Item, Composition
from mirusers.models import Hub, MirUser


class ItemModelSerializerSNS(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('uid', 'sku', 'unitOfMeasure', 'batch')


class CompositionModelSerializerSNS(serializers.ModelSerializer):
    sUSNSet = ItemModelSerializerSNS(many=True)

    class Meta:
        model = Composition
        fields = ('sku', 'amount', 'unitOfMeasure', 'sUSNSet')


class OrderModelSerializerSNS(serializers.ModelSerializer):
    hub = serializers.CharField()
    sPositionSet = CompositionModelSerializerSNS(many=True)

    def validate_hub(self, value):
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

    def create(self, validated_data):
        sPositionSet = validated_data.pop('sPositionSet')
        order = Order(**validated_data)
        compositions = list()
        items = list()
        for position in sPositionSet:
            sUSNSet = position.pop('sUSNSet')
            if position['amount'] != len(sUSNSet):
                raise serializers.ValidationError('The amount does not match the number of items')
            composition = Composition(order=order, **position)
            compositions.append(composition)
            for usnset in sUSNSet:
                item = Item(composition=composition, **usnset)
                items.append(item)
        order.save()
        Composition.objects.bulk_create(compositions)
        Item.objects.bulk_create(items)
        return order

    class Meta:
        model = Order
        fields = '__all__'

import datetime

from rest_framework import serializers
from hub_api.models import Order, Item, Composition
from mirusers.models import Hub, MirUser


def uid_normalization(uid, unitOfMeasure):
    if unitOfMeasure == 'case':
        return f"{uid[:16]}{uid[26:47]}"
    elif unitOfMeasure == 'out':
        return f"{uid[:25]}"
    else:
        return uid


# send order from HUBs for tracking prodict

class ItemModelSerializer(serializers.ModelSerializer):

    def validate_uid(self, value):
        if len(value) == 67 and str(value[44:47]) == "500":
            return value
        elif len(value) == 52 and str(value[25:29]) == "8005":
            return value
        else:
            raise serializers.ValidationError('Looks like the wrong CASE or OUTER code is intended to be transmitted')

    class Meta:
        model = Item
        fields = ('uid', 'sku', 'unitOfMeasure', 'batch')


class CompositionModelSerializer(serializers.ModelSerializer):
    sUSNSet = ItemModelSerializer(many=True)

    class Meta:
        model = Composition
        fields = ('sku', 'amount', 'unitOfMeasure', 'sUSNSet')


class OrderModelSerializer(serializers.ModelSerializer):
    hub = serializers.CharField()
    sPositionSet = CompositionModelSerializer(many=True)

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

    def validate_sPositionSet(self, value):
        items = list()
        for position in value:
            for item in position['sUSNSet']:
                items.append(item['uid'])
        if len(items) == len(set(items)):
            return value
        else:
            raise serializers.ValidationError('You seem to have duplicate codes in the order')

    def validate_buyoutDate(self, value):
        if value > datetime.date.today():
            return value
        else:
            raise serializers.ValidationError('The date must not be in the past or today')

    def create(self, validated_data):
        sPositionSet = validated_data.pop('sPositionSet')
        order = Order.objects.create(**validated_data)
        items = list()
        for position in sPositionSet:
            sUSNSet = position.pop('sUSNSet')
            if position['amount'] != len(sUSNSet):
                order.delete()
                raise serializers.ValidationError('The amount does not match the number of items')
            composition = Composition.objects.create(order=order, **position)
            for usnset in sUSNSet:
                item = Item(composition=composition, tuid=uid_normalization(usnset['uid'], usnset['unitOfMeasure']),
                            **usnset)
                items.append(item)
        Item.objects.bulk_create(items)
        return order

    class Meta:
        model = Order
        fields = '__all__'


class CompositionNonTNTModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition
        fields = ('sku', 'amount', 'unitOfMeasure')


class OrderNonTNTModelSerializer(serializers.ModelSerializer):
    hub = serializers.CharField()
    sPositionSet = CompositionNonTNTModelSerializer(many=True)

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

    def validate_buyoutDate(self, value):
        if value > datetime.date.today():
            return value
        else:
            raise serializers.ValidationError('The date must not be in the past or today')

    def create(self, validated_data):
        sPositionSet = validated_data.pop('sPositionSet')
        order = Order.objects.create(**validated_data)
        compositions = list()
        for position in sPositionSet:
            composition = Composition(order=order, **position)
            compositions.append(composition)
        Composition.objects.bulk_create(compositions)
        return order

    class Meta:
        model = Order
        fields = '__all__'


# section for codes validation via Sputnik


class OrderForSputnikListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'order', 'saleType', 'validation_uuid', 'status')


class OrderForSputnikUUIDUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('validation_uuid', 'status')


class ItemValidationForSputnikRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('tuid',)


class CompositionValidationForSputnikRetrieveSerializer(serializers.ModelSerializer):
    sUSNSet = serializers.StringRelatedField(many=True)

    class Meta:
        model = Composition
        fields = ('sUSNSet',)


class OrderValidationForSputnikRetrieveSerializer(serializers.ModelSerializer):
    sPositionSet = CompositionValidationForSputnikRetrieveSerializer(many=True)

    class Meta:
        model = Order
        fields = ('order', 'saleType', 'sPositionSet',)

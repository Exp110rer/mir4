from rest_framework import serializers
from ext_tnt.models import Aggregation, Unit, Item
import uuid


class ItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('unitSerialNumber', 'id')


class UnitModelSerializer(serializers.ModelSerializer):
    sntins = serializers.ListSerializer(child=serializers.CharField())

    class Meta:
        model = Unit
        fields = (
            'unitSerialNumber', 'aggregatedItemsCount', 'aggregationType', 'aggregationUnitCapacity',
            'sntins')


class AggregationModelSerializer(serializers.ModelSerializer):
    aggregationUnits = UnitModelSerializer(many=True)

    def create(self, validated_data):
        aggregation_uuid = self.initial_data['aggregation_uuid']
        validated_data['uuid'] = aggregation_uuid
        aggregationUnits = validated_data.pop('aggregationUnits')
        aggregation = Aggregation.objects.create(**validated_data)
        items = list()
        for aggregationUnit in aggregationUnits:
            aggregationUnit['uuid'] = aggregation_uuid
            sntins = aggregationUnit.pop('sntins')
            unit = Unit.objects.create(aggregation=aggregation, **aggregationUnit)
            for sntin in sntins:
                items.append(Item(unitSerialNumber=sntin, uuid=aggregation_uuid, aggregation=aggregation, unit=unit))
        Item.objects.bulk_create(items)
        print('OK posle aggreg')
        return aggregation

    class Meta:
        model = Aggregation
        fields = ('participantId', 'productionLineId', 'sku', 'batch', 'aggregationUnits', 'updatedBy')

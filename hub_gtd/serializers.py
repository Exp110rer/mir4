import django.db.utils
from rest_framework import serializers
from hub_gtd.models import Item, SKU, GTD
from uuid import uuid4


class TUIDsListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(gtd_id=self.context.get('gtd', 0))
        return super().to_representation(data)


class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        return instance.tuid

    def to_internal_value(self, data):
        return data

    class Meta:
        model = Item
        fields = '__all__'
        list_serializer_class = TUIDsListSerializer


class SKUSerializer(serializers.ModelSerializer):
    tuids = ItemSerializer(many=True)

    class Meta:
        model = SKU
        fields = ('sku', 'tuids',)

    def validate_tuids(self, value):
        tuids_not_valid_list = [item for item in value if len(item) != 37 or item[-3:] != "500"]
        if len(tuids_not_valid_list) > 0:
            raise serializers.ValidationError(f'Not valid TNT  codes ---> {tuids_not_valid_list}')
        return value


class GTDSerializer(serializers.ModelSerializer):
    items = SKUSerializer(many=True)

    class Meta:
        model = GTD
        fields = ('gtd', 'items')

    def validate(self, data):
        items_in_data = list()
        for item in data['items']:
            items_in_data.extend(item['tuids'])
        if len(items_in_data) != len(set(items_in_data)):
            raise serializers.ValidationError("Duplicate TNT codes")
        return data

    def create(self, validated_data):
        items = validated_data.pop('items')
        if not GTD.objects.filter(**validated_data).exists():
            gtd = GTD.objects.create(**validated_data, guid=uuid4())
            gtd_creation_flag = True
        else:
            gtd = GTD.objects.get(**validated_data)
            gtd_creation_flag = False
        items_list = list()
        sku_list = list()
        for item in items:
            sku, sku_creation_flag = SKU.objects.get_or_create(sku=item['sku'])
            if sku_creation_flag:
                sku_list.append(sku)
            sku.gtd.add(gtd)
            items_set = [Item(tuid=tuid, gtd=gtd, sku=sku) for tuid in item['tuids']]
            items_list.extend(items_set)
        try:
            Item.objects.bulk_create(items_list)
        except django.db.utils.IntegrityError as E:
            if gtd_creation_flag:
                gtd.delete()
            for sku in sku_list:
                sku.delete()
            tuids_list = [item.tuid for item in items_list]
            items_in_list = Item.objects.filter(tuid__in=tuids_list)
            error_message = dict()
            error_message['status'] = 'Error'
            error_message['details'] = dict()
            for item in items_in_list:
                error_message['details'][item.tuid] = item.gtd
            raise serializers.ValidationError(error_message)
        return gtd

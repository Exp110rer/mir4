import datetime

from rest_framework import serializers
from hub_api.models import Order, Item, Composition, ProductCategory
from hub_gtd.models import Item as GTD_Item, SKU
from mirusers.models import Hub, MirUser


def uid_normalization(uid, unitOfMeasure):
    if unitOfMeasure == 'case':
        return f"{uid[:16]}{uid[26:47]}"
    elif unitOfMeasure == 'out':
        return f"{uid[:25]}"
    else:
        return uid


def gtd_update(item: GTD_Item, gtd_tuids_gtds):
    item.gtd = gtd_tuids_gtds.get(item.tuid)
    return item


# send order from HUBs for tracking prodict

class ItemIsValidListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(validity=1)
        return super().to_representation(data)


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
        list_serializer_class = ItemIsValidListSerializer


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

    # def validate_buyoutDate(self, value):
    #     if value > datetime.date.today():
    #         return value
    #     else:
    #         raise serializers.ValidationError('The date must not be in the past or today')

    def validate_productCategory(self, value):
        try:
            productCategory = ProductCategory.objects.get(name=value)
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError('The specified productCategory does not exists.')
        else:
            if productCategory.traceability == 1:
                return value
            else:
                raise serializers.ValidationError(f"Product category {value} is not traceable.")

    def validate_customerOrderNumber(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(f"Ensure customerOrderNumber field has 10 characters.")
        else:
            return value

    def create(self, validated_data):
        sPositionSet = validated_data.pop('sPositionSet')
        order = Order.objects.create(**validated_data)
        items = list()
        gtd_skus = [sku.sku for sku in SKU.objects.all()]
        print(gtd_skus)
        for position in sPositionSet:
            sUSNSet = position.pop('sUSNSet')
            if position['amount'] != len(sUSNSet):
                order.delete()
                raise serializers.ValidationError('The amount does not match the number of items')
            composition = Composition.objects.create(order=order, **position)
            items_set = list()
            for usnset in sUSNSet:
                tuid = uid_normalization(usnset['uid'], usnset['unitOfMeasure'])
                item = Item(composition=composition, tuid=tuid, **usnset)
                items_set.append(item)
            if position['sku'] in gtd_skus:
                gtd_tuids = [item.tuid for item in items_set]
                gtd_tuids_gtds = {item.tuid: item.gtd.gtd for item in GTD_Item.objects.filter(tuid__in=gtd_tuids)}
                items_set = [gtd_update(item_set, gtd_tuids_gtds) for item_set in items_set]
            items.extend(items_set)
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

    # def validate_buyoutDate(self, value):
    #     if value > datetime.date.today():
    #         return value
    #     else:
    #         raise serializers.ValidationError('The date must not be in the past or today')

    def validate_productCategory(self, value):
        try:
            productCategory = ProductCategory.objects.get(name=value)
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError('The specified productCategory does not exists.')
        else:
            if productCategory.traceability == 0:
                return value
            else:
                raise serializers.ValidationError(f"Product category {value} is traceable.")

    def validate_customerOrderNumber(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(f"Ensure customerOrderNumber field has 10 characters.")
        else:
            return value

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


class ItemGetERPModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('tuid', 'unitOfMeasure', 'sku', 'batch', 'gtd')
        list_serializer_class = ItemIsValidListSerializer


class CompositionGetERPModelSerializer(serializers.ModelSerializer):
    sUSNSet = ItemGetERPModelSerializer(many=True, read_only=True)

    class Meta:
        model = Composition
        fields = ('sku', 'unitOfMeasure', 'sUSNSet')


class OrderGetERPModelSerializer(serializers.ModelSerializer):
    sPositionSet = CompositionGetERPModelSerializer(many=True, read_only=True)
    hub = serializers.CharField()

    class Meta:
        model = Order
        exclude = (
            'id', 'validation_uuid', 'updatedBy', 'downloadedBy', 'itemsCount', 'partial', 'iteration')


class ItemIsNotValidListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(validity=0)
        return super().to_representation(data)


class ItemGetModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('uid',)
        list_serializer_class = ItemIsNotValidListSerializer


class CompositionGetModelSerializer(serializers.ModelSerializer):
    sUSNSet = ItemGetModelSerializer(many=True, read_only=True)

    class Meta:
        model = Composition
        fields = ('sku', 'unitOfMeasure', 'sUSNSet')


class OrderGetModelSerializer(serializers.ModelSerializer):
    sPositionSet = CompositionGetModelSerializer(many=True, read_only=True)
    hub = serializers.CharField()
    ERPLockStatus = serializers.SerializerMethodField('partial_func')

    def partial_func(self, obj):
        if obj.partial is True:
            return 'LOCKED'
        else:
            return 'OPEN'

    class Meta:
        model = Order
        exclude = (
            'id', 'validation_uuid', 'deleted', 'updatedBy', 'downloadedBy', 'itemsCount', 'iteration',)


class OrdersUpdateBy1CModelSerializer(serializers.ModelSerializer):

    def validate_cs1CUnloadStatus(self, value):
        if value is True:
            return value
        else:
            raise serializers.ValidationError('The only "true" value is accepted for cs1UploadStatus ')

    def validate_cs1CProcessingStatus(self, value):
        if value == "" or value is None:
            raise serializers.ValidationError('The only "OK" or "NOK" values are accepted for cs1CProcessingStatus ')
        else:
            return value

    class Meta:
        model = Order
        fields = ('cs1CUnloadStatus', 'cs1CProcessingStatus')
        extra_kwargs = {'cs1CUnloadStatus': {'required': True}, 'cs1CProcessingStatus': {'required': True}}

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

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.renderers import JSONRenderer
from hub_api.models import Order, Item
from hub_api.serializers import OrderModelSerializer, ItemModelSerializer

SUCCESS_RESPONSE = {"status": "processed"}
NO_PERMISSION_RESPONSE = {"detail": "You do not have permission to perform this action."}


class OrderCreateModelViewSet(CreateModelMixin, GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderModelSerializer
    permission_classes = [DjangoModelPermissions]
    renderer_classes = [JSONRenderer]

    def create(self, request, *args, **kwargs):
        data = request.data
        data['updatedBy'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(SUCCESS_RESPONSE, status=status.HTTP_201_CREATED, headers=headers)


class ItemCreateModelViewSet(CreateModelMixin, GenericViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemModelSerializer
    permission_classes = [DjangoModelPermissions]


class OrderRetrieveModelViewSet(RetrieveModelMixin, GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderModelSerializer
    permission_classes = [DjangoModelPermissions]
    lookup_field = 'order'

    def retrieve(self, request, *args, **kwargs):
        if request.user.groups.filter(name='ERP_Executives').exists():
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            sku = dict()
            for item in data.pop('items'):
                sku_number = item.pop('sku')
                sku.setdefault(sku_number, [])
                sku[sku_number].append(item)
            data['sku'] = sku
            return Response(data)
        else:
            return Response(NO_PERMISSION_RESPONSE, status=status.HTTP_403_FORBIDDEN)

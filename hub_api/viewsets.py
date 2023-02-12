from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from hub_api.models import Order, Item
from hub_api.serializers import OrderModelSerializer, ItemModelSerializer


SUCCESS_RESPONSE = {"status": "processed"}


class OrderModelViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
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


class ItemModelViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemModelSerializer
    permission_classes = [DjangoModelPermissions]

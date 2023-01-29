from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from hub_api.models import Order, Item
from hub_api.serializers import OrderModelSerializer, ItemModelSerializer


class OrderModelViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderModelSerializer

    def create(self, request, *args, **kwargs):
        try:
            items_list = request.data.pop('items')
        except KeyError:
            pass
        else:
            items_dict = [{"uid": item} for item in items_list]
            request.data['items'] = items_dict
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response("ok", status=status.HTTP_201_CREATED, headers=headers)


class ItemModelViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemModelSerializer

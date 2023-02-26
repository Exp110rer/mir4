from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import DjangoModelPermissions
from hub_api.models import Order
from hub_api.serializers import OrderModelSerializerSNS
from django.shortcuts import get_object_or_404

SUCCESS_RESPONSE = {"status": "processed"}
NO_PERMISSION_RESPONSE = {"details": "You do not have permission to perform this action."}


class OrderCreateModelViewSetSNS(CreateModelMixin, GenericViewSet):
    serializer_class = OrderModelSerializerSNS
    queryset = Order.objects.all()
    permission_classes = [DjangoModelPermissions]

    def create(self, request, *args, **kwargs):
        data = request.data
        data['updatedBy'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(SUCCESS_RESPONSE, status=status.HTTP_201_CREATED, headers=headers)


class OrderRetrieveModelViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = OrderModelSerializerSNS
    queryset = Order.objects.all()
    permission_classes = [DjangoModelPermissions]
    lookup_field = 'order'

    def get_object(self):

        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg],
                         'saleType': self.request.GET.get('saleType', 'RU')}

        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj

    def retrieve(self, request, *args, **kwargs):
        if request.user.groups.filter(name='ERP_Executives').exists():
            return super().retrieve(request)
        else:
            return Response(NO_PERMISSION_RESPONSE, status=status.HTTP_403_FORBIDDEN)

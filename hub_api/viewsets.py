from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.authentication import BasicAuthentication
from hub_api.models import Order, Item
from hub_api.serializers import OrderModelSerializer, OrderNonTNTModelSerializer, OrderForSputnikListSerializer, \
    OrderForSputnikUUIDUpdateSerializer, OrderValidationForSputnikRetrieveSerializer, OrderGetModelSerializer, \
    OrderGetERPModelSerializer
from rest_framework.serializers import ValidationError
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from .utils import ihubzone_send_mail

SUCCESS_RESPONSE = {"status": "processed"}
DELETE_RESPONSE = {"status": "deleted"}
FAILURE_RESPONSE = {"status": "error processing"}
NO_PERMISSION_RESPONSE = {"details": "You DO NOT have permission to perform this action."}
ORDER_STATUS = {0: 'not verified', 1: 'verification is in progress', 4: 'Suspicious'}


class OrderCreateModelViewSetSNS(CreateModelMixin, GenericViewSet):
    serializer_class = OrderModelSerializer
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
    serializer_class = OrderGetERPModelSerializer
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
            instance = self.get_object()
            if instance.deleted:
                return Response({"order": instance.order, "status": "Deleted"},
                                status.HTTP_200_OK)
            if instance.status != 2:
                return Response({"order": instance.order, "status": ORDER_STATUS[instance.status]},
                                status.HTTP_200_OK)
            serializer = self.get_serializer(instance)
            instance.partial = True
            instance.save(update_fields=['partial'])
            return Response(serializer.data)
        else:
            return Response(NO_PERMISSION_RESPONSE, status=status.HTTP_403_FORBIDDEN)


class OrderCreateNonTNTModelViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = OrderNonTNTModelSerializer
    queryset = Order.objects.all()
    permission_classes = [DjangoModelPermissions]

    def create(self, request, *args, **kwargs):
        data = request.data
        data['updatedBy'] = request.user.id
        data['status'] = 2
        data['traceability'] = False
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        ihubzone_send_mail(serializer.data, status='received')
        return Response(SUCCESS_RESPONSE, status=status.HTTP_201_CREATED, headers=headers)


class OrderRetrieveNonERPModelViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = OrderGetModelSerializer
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
        if request.user.groups.filter(name='HUB_Executives'):
            instance = self.get_object()
            if instance.deleted is True:
                return Response({"order": instance.order, "status": "Deleted"}, status.HTTP_200_OK)
            if instance.status != 2:
                return Response({"order": instance.order, "status": ORDER_STATUS[instance.status]}, status.HTTP_200_OK)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response(NO_PERMISSION_RESPONSE, status.HTTP_403_FORBIDDEN)


class OrderDeleteModelViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = OrderModelSerializer
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
        if request.user.groups.filter(name='HUB_Executives').exists():
            instance = self.get_object()
            if instance.partial is True:
                return Response({"status": f"Order {instance.order} is locked"}, status=status.HTTP_423_LOCKED)
            if instance.deleted is True:
                return Response({"status": f"Order {instance.order} has already been deleted"},
                                status=status.HTTP_200_OK)
            instance.deleted = True
            instance.save(update_fields=['deleted'])
            ihubzone_send_mail(instance, status='deleted')
            return Response(DELETE_RESPONSE, status=status.HTTP_200_OK)
        else:
            return Response(NO_PERMISSION_RESPONSE, status=status.HTTP_403_FORBIDDEN)


# section for codes validation via Sputnik

class OrderForSputnikListViewSet(ListModelMixin, GenericViewSet):
    serializer_class = OrderForSputnikListSerializer
    queryset = Order.objects.filter(status__in=(0, 1), deleted=False)
    authentication_classes = [BasicAuthentication]
    permission_classes = [DjangoModelPermissions]

    def list(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Validator'):
            return super().list(request, args, kwargs)
        else:
            return Response(NO_PERMISSION_RESPONSE, status=status.HTTP_403_FORBIDDEN)


class OrderForSputnikUUIDUpdateViewSet(UpdateModelMixin, GenericViewSet):
    serializer_class = OrderForSputnikUUIDUpdateSerializer
    queryset = Order.objects.exclude(status=2)
    authentication_classes = [BasicAuthentication]
    permission_classes = [DjangoModelPermissions]

    def update(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Validator').exists():
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            data = request.data
            data['status'] = 1
            print(data)
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            return Response(NO_PERMISSION_RESPONSE, status=status.HTTP_403_FORBIDDEN)


class OrderForSputnikRetrieveViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = OrderValidationForSputnikRetrieveSerializer
    queryset = Order.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [DjangoModelPermissions]

    def retrieve(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Validator'):
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            serializer_data = serializer.data
            response_data = dict()
            response_data['codes'] = list()
            for item in serializer_data['sPositionSet']:
                response_data['codes'].extend(item['sUSNSet'])
            response_data['ownerInn'] = '7809008119' if serializer_data['saleType'] == 'RU12' else '7705060700'
            response_data['shipToParty'] = 'ITMS' if serializer_data['saleType'] == 'RU12' else 'SNS'
            response_data['delivery'] = serializer_data['order']
            return Response(response_data)
        else:
            return Response(NO_PERMISSION_RESPONSE, status=status.HTTP_403_FORBIDDEN)


class OrderForSputnikCodeValidityUpdateViewSet(CreateModelMixin, GenericViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [DjangoModelPermissions]
    queryset = Order.objects.all()

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Validator'):
            order_id = request.data.get('id', None)
            cisInfo = request.data.get('cisInfo', None)

            if all((order_id, isinstance(cisInfo, dict))):
                items = list()
                try:
                    order = Order.objects.get(id=order_id)
                except Order.DoesNotExist:
                    return Response({"status": f"order with ID {order_id} is not found"},
                                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                sputnik_health_check = set(cisInfo.values())
                if len(sputnik_health_check) == 1 and sputnik_health_check == {'NOK'}:
                    order.status = 4
                else:
                    for tuid, tuid_status in cisInfo.items():
                        try:
                            item = Item.objects.get(composition__order=order, tuid=tuid)
                        except Item.DoesNotExist:
                            return Response({"status": f"tuid {tuid} is not found in order {order.order}"},
                                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                        else:
                            item.validity = 1 if tuid_status == 'OK' else 0
                            items.append(item)
                    Item.objects.bulk_update(items, fields=('validity',))
                    order.status = 2
                    # send mail
                order.save()
                ihubzone_send_mail(order, status='validated')
                return Response(SUCCESS_RESPONSE, status=status.HTTP_200_OK)
            else:
                return Response(FAILURE_RESPONSE, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(NO_PERMISSION_RESPONSE, status=status.HTTP_403_FORBIDDEN)

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework import status
from ext_tnt.serializers import AggregationModelSerializer
from ext_tnt.models import Aggregation
import uuid

NO_PERMISSION_RESPONSE = {"details": "You do not have permission to perform this action."}


class AggregationRetrieveModelViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = AggregationModelSerializer
    queryset = Aggregation.objects.all()
    permission_classes = [DjangoModelPermissions]
    lookup_field = 'uuid'

    def retrieve(self, request, *args, **kwargs):
        if request.user.groups.filter(name='FACTORY_Executives').exists():
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response(NO_PERMISSION_RESPONSE, status=status.HTTP_403_FORBIDDEN)


class AggregationCreateModelViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = AggregationModelSerializer
    queryset = Aggregation.objects.all()
    permission_classes = [DjangoModelPermissions]

    def create(self, request, *args, **kwargs):
        aggregation_uuid = uuid.uuid4()
        # request.data['aggregation_uuid'] = aggregation_uuid
        request.data['uuid'] = aggregation_uuid
        request.data['updatedBy'] = request.user.username
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = {'uuid': aggregation_uuid}
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

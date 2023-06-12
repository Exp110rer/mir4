from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework import status
from hub_gtd.models import GTD
from hub_gtd.serializers import GTDSerializer


class SendGTDViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = GTDSerializer
    queryset = GTD.objects.all()
    permission_classes = [DjangoModelPermissions]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        message = dict()
        message['status'] = 'Success'
        message['GTD guid'] = GTD.objects.get(gtd=serializer.data['gtd']).guid
        return Response(message, status=status.HTTP_201_CREATED, headers=headers)


class GetGTDViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = GTDSerializer
    queryset = GTD.objects.all()
    permission_classes = [DjangoModelPermissions]
    lookup_field = 'guid'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['gtd'] = self.get_object()
        return context

    def retrieve(self, request, *args, **kwargs):
        message = {"detail": "You do not have permission to perform this action."}
        if request.user.groups.filter(name='GTD_Executives').exists():
            return super().retrieve(request)
        else:
            return Response(message, status=status.HTTP_403_FORBIDDEN)


from django.urls import path, include
from hub_api.apps import HubApiConfig
from hub_api.viewsets import OrderModelViewSet, ItemModelViewSet
from rest_framework.routers import DefaultRouter

app_name = HubApiConfig.name

router_hub_api = DefaultRouter()
router_hub_api.register('orders', OrderModelViewSet)
router_hub_api.register('items', ItemModelViewSet)

urlpatterns = [
    path('', include(router_hub_api.urls)),
]

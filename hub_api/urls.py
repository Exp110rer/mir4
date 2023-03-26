from django.urls import path, include
from hub_api.apps import HubApiConfig
from hub_api.viewsets import OrderCreateModelViewSetSNS, OrderRetrieveModelViewSet, OrderCreateNonTNTModelViewSet, \
    OrderForSputnikListViewSet, OrderForSputnikRetrieveViewSet, OrderForSputnikUUIDUpdateViewSet, OrderForSputnikCodeValidityUpdateViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from rest_framework_simplejwt.views import TokenObtainSlidingView

app_name = HubApiConfig.name

router_hub_api = DefaultRouter()
router_hub_api.register('sOrder', OrderCreateModelViewSetSNS)
router_hub_api.register('gOrder', OrderRetrieveModelViewSet)
router_hub_api.register('sOrderNonTnt', OrderCreateNonTNTModelViewSet)

router_hub_api_validation = DefaultRouter()
router_hub_api_validation.register('list', OrderForSputnikListViewSet)
router_hub_api_validation.register('uuidupdate', OrderForSputnikUUIDUpdateViewSet)
router_hub_api_validation.register('retrieve', OrderForSputnikRetrieveViewSet)
router_hub_api_validation.register('valupdate', OrderForSputnikCodeValidityUpdateViewSet, basename='ValUpdate')

urlpatterns = [
    path('', include(router_hub_api.urls), name='hub_api'),
    path('validation/', include(router_hub_api_validation.urls), name='validation'),
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
    path('auth/', TokenObtainSlidingView.as_view()),
]

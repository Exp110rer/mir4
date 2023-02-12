from django.urls import path, include
from hub_api.apps import HubApiConfig
from hub_api.viewsets import OrderModelViewSet, ItemModelViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from rest_framework_simplejwt.views import TokenObtainSlidingView

app_name = HubApiConfig.name

router_hub_api = DefaultRouter()
router_hub_api.register('orders', OrderModelViewSet)
router_hub_api.register('items', ItemModelViewSet)

urlpatterns = [
    path('', include(router_hub_api.urls), name='hub_api'),
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
    path('auth/', TokenObtainSlidingView.as_view()),
]

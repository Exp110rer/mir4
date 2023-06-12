from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hub_gtd.viewsets import SendGTDViewSet, GetGTDViewSet
from hub_gtd.apps import HubGtdConfig

app_name = HubGtdConfig.name

router_hub_gtd = DefaultRouter()
router_hub_gtd.register('sGTD', SendGTDViewSet)
router_hub_gtd.register('gGTD', GetGTDViewSet)

urlpatterns = [
    path('', include(router_hub_gtd.urls), name='hub_gtd'),
]



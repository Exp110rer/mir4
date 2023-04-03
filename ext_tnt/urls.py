from django.urls import path, include
from ext_tnt.apps import ExtTntConfig
from ext_tnt.viewsets import AggregationCreateModelViewSet, AggregationRetrieveModelViewSet
from rest_framework.routers import SimpleRouter


app_name = ExtTntConfig.name

ext_tnt_router = SimpleRouter()
ext_tnt_router.register('gAggregation', AggregationRetrieveModelViewSet)
ext_tnt_router.register('sAggregation', AggregationCreateModelViewSet)

urlpatterns = [
    path('', include(ext_tnt_router.urls), name='ext_tnt'),
]



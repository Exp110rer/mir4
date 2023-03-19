from django.urls import path
from hub_portal.apps import HubPortalConfig
from django.views.generic import TemplateView
from hub_portal.views import OrderBCPListView, OrderBCPDetailView, OrderCSListView, OrderCSDetailView

app_name = HubPortalConfig.name

urlpatterns = [
    path('bcp/<int:pk>/', OrderBCPDetailView.as_view(), name='bcp_excel'),
    path('cs/<int:pk>/', OrderCSDetailView.as_view(), name='cs_excel'),
    path('bcp/', OrderBCPListView.as_view(), name='orders_bcp'),
    path('cs/', OrderCSListView.as_view(), name='orders_cs'),
]

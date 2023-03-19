from django.urls import path
from mirusers.apps import MirusersConfig
from mirusers.views import MirUserLoginView, MirUserLogoutView

app_name = MirusersConfig.name

urlpatterns = [
    path('login/', MirUserLoginView.as_view(), name='login'),
    path('logout/', MirUserLogoutView.as_view(), name='logout'),
]
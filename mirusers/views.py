from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse, reverse_lazy
from django.contrib import messages


# Create your views here.

class MirUserLoginView(LoginView):

    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.groups.filter(name='Orders_BCP').exists():
            return reverse_lazy('hub_portal:orders_cs')
        elif self.request.user.groups.filter(name='Orders_CS').exists():
            return reverse_lazy('hub_portal:orders_cs')
        else:
            return reverse_lazy('main')

    template_name = 'mirusers/login.html'


class MirUserLogoutView(LogoutView):
    next_page = reverse_lazy('mirusers:login')

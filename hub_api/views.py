from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.

def entry_start(request):
    return HttpResponse('OK')

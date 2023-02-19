from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.

def entry_start(request):
    return HttpResponse('OK')



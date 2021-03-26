from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# Create your views here.


def add(request):
    return HttpResponse("<html><body>register new commodities</body></html>")


def detail(request, id):
    return HttpResponse("<html><body>Get for commodities detail %d</body></html>" % id)

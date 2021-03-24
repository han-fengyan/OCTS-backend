from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User


# Create your views here.


def main_view(request):
    return HttpResponse("<html><body>Hello</body></html>")


def login(request):
    def gen_response(code: int, data: str):
        return JsonResponse({
            'code': code,
            'data': data
        }, status=code)
    if request.method == 'POST':
        pass

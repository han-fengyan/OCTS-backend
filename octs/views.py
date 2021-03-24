from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json
from .models import User
from django.core.exceptions import ValidationError

# Create your views here.


def main_view(request):
    return HttpResponse("<html><body>Hello</body></html>")


def signup(request):
    def gen_response(code: int, data: str):
        return JsonResponse({
            'code': code,
            'data': data
        }, status=code)

    if request.method == 'POST':
        request_data =request.body
        json_str = request_data.decode()

    #判断前端发来的数据是否合法
    try:
        json_data = json.loads(json_str)
            username = json_data['username']
            password = json_data['password']
        except Exception as e:
            return gen_response(400, "message is invalid")

        #需要判断是否已经有重复用户名，并将查询结果返回前端
        inuser = User.objects.filter(user=username)
        if inuser:
            return gen_response(406,'user has existed')
        else:
            user = User(name = username, password = password)
            user.save()
            return gen_response(201,"sign up successfully")


def login(request):
    def gen_response(code: int, data: str):
        return JsonResponse({
            'code': code,
            'data': data
        }, status=code)

    if request.method == 'POST':
        pass

from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from .models import User
import json
import jwt
# from rest_framework_jwt.settings import api_settings
# Create your views here.


def main_view(request):
    return HttpResponse("<html><body><center>Hello</center></body></html>")

def gen_response(code: int, data: str):
        return JsonResponse({
            'code': code,
            'data': data
        }, status=code)

@csrf_exempt
def signup(request):
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
        
        if username is None or password is None:
            return gen_response(400, "message is invalid")

        #需要判断是否已经有重复用户名，并将查询结果返回前端
        inuser = User.objects.filter(name=username)
        if inuser:
            return gen_response(406,'user has existed')
        else:
            user = User(name = username, password = password)
            user.save()
            return gen_response(201,"sign up successfully")

@csrf_exempt
def login(request):
    
    if request.method == 'POST':
        json_str = request.body.decode()
        json_data = json.loads(json_str)

        try:
            user = User.objects.get(name = json_data['username']) 
        except Exception as e:
            return gen_response(400, "user doesn't exist")

        if user.password == json_data['password']:
            user.token = user.token(self)    
            return JsonResponse({'code':201, 'data':"login successfully",'token': user.token})
        else:
            return gen_response(401, "password is wrong!")

def order(requset):

    if request.method == 'POST':
        pass
from django.http import JsonResponse, HttpResponse
from http import HTTPStatus
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from .models import User, Coupon ,Order
from goods.models import Good, Picture

from django.conf import settings
import datetime,time,random
import json
import jwt
# Create your views here.

def main_view(request):
    return HttpResponse("<html><body>Hello</body></html>")

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
        except Exception :
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
        except Exception :
            return gen_response(400, "user doesn't exist")

        if user.password == json_data['password']:
            #创建token
            dic = {
                'exp': datetime.datetime.now() + datetime.timedelta(days=1), #过期时间
                'iat': datetime.datetime.now(),#开始时间
                'username': user.name
            }
            s = jwt.encode(dic, settings.SECRET_KEY, algorithm='HS256')
            user.token = s
            user.save()
            return JsonResponse({'code':201, 'data':"login successfully",'token': s , 'money': user.money, 'name':user.name})
                    
        else:
            return gen_response(401, "password is wrong!")

@csrf_exempt
def order(request):
    #禁止使用get来下单
    if request.method != 'POST':
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,
                            "please place your order with post")
    
    if request.method == 'POST':
        #是否为json表单
        try:
            json_data = json.loads(request.body.decode('utf-8'))
        except ValueError :
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype") 
        
        #判断前端发来的数据是否合法
        try:
            username = json_data['username']
            goodid = json_data['goodid']
            count = json_data['count']

        except KeyError as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "key message is wrong")
        except Exception as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid")    
        #判断数据库是否有该用户或者商品
        try:
            user = User.objects.get(name = username)    
            good = Good.objects.get(id = goodid)
        except Exception as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "user or good doesn't exist") 
        
        #判断商品是否上架
        if good.available is False:
            return gen_response(406, "the good is off shelf") 

        #判断商品存货、用户余额
        money = user.money
        now_price = good.discount
        if money < now_price * count :
            return gen_response(406, "money is not enough")
        if count > good.quantities_of_inventory:
            return gen_response(406, "quantity of goods is not enough")
        #更新商品与用户信息
        good.quantities_of_inventory -= count
        good.quantities_sold += count
        good.save()

        # user.money -= count * now_price
        # user.save()
        id = str(time.time())[6:10]+str(time.time())[11:18] + str(random.randint(10,99)) + str(goodid) + str(random.randint(10,99)) 
        Order.objects.create(user=user, orderid=id, goodid=goodid, name=good.name, count=count, cost = count * now_price , state = 0)
        return gen_response(200, id)


@csrf_exempt
def pay(request):
    if request.method != 'POST':
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,
                        "please place your order with post")
    
    if request.method == 'POST':
        #是否为json表单
        try:
            json_data = json.loads(request.body.decode('utf-8'))
        except ValueError as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype")
        
        #判断前端发来的数据是否合法
        try:
            username = json_data['username']
            orderid = json_data['orderid']
            cost = json_data['cost']

        except KeyError as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "key message is wrong")
        except Exception as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid")  
        
        #判断数据库是否有该用户或者商品
        try:
            user = User.objects.get(name = username)    
            order = Order.objects.get(orderid = orderid)
        except Exception as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "user or order doesn't exist") 
        
        if user.money < cost :
            return gen_response(HTTPStatus.BAD_REQUEST, "money is not enough")
        
        if order.state == 0:
            order.state = 1
            order.save()
        else:
            return gen_response(HTTPStatus.BAD_REQUEST,"your order has been paid")

        user.money -= cost
        user.save()

        return gen_response(200,"you have paid successfully")


@csrf_exempt
def userorder(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))

        except ValueError as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype") 
        
        try:
            user = json_data['username']
            
        except KeyError as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "key message is wrong")
        except Exception as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid") 

        user = User.objects.get(name=user)
        orderlist = Order.objects.filter(user=user)
        return gen_response(200, [
                {
                    'name': order.name,
                    'count': order.count,
                    'orderid': order.orderid,
                    'goodid': order.goodid,
                    'cost': order.cost,
                    'date': int(order.pub_date.timestamp()),
                    'state': order.state,
                }
                for order in orderlist.order_by('-id')
            ])

    return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,"please place your order with post")

@csrf_exempt
def orderlist(request):
    if request.method == 'GET':
        #检验商家身份》待做
        orderlist = Order.objects.all()
        return gen_response(200, [
                {
                    'user': order.user.name,
                    'orderid': order.orderid,
                    'goodid': order.goodid,
                    'name': order.name,
                    'count': order.count,
                    'cost': order.cost,
                    'date': int(order.pub_date.timestamp()),
                    'state': order.state,
                }

             
                for order in orderlist.order_by('-id')
            ])

@csrf_exempt
def orderstate(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))

        except ValueError as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype") 
        
        try:
            orderid = json_data['orderid']
            change = json_data['change']

        except KeyError as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "key message is wrong")
        except Exception as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid") 

        try:
            order = Order.objects.get(orderid = orderid)
        except Exception as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "order doesn't exist")   

        order.state = change
        order.save()
        return gen_response(200,"you have modify the order successfully")

    return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,"please modify an order with post")
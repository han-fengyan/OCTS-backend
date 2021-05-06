from django.http import JsonResponse, HttpResponse
from http import HTTPStatus
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from .models import User, Coupon ,Order,Merchant
from goods.models import Good, Picture

from django.conf import settings
import datetime,time,random
import json
import jwt
# Create your views here.

def gen_response(code, data):
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
                'exp': time.time() + 23200, #过期时间
                # 'iat': time.time(),#开始时间
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
            token = json_data['token']

        except Exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid") 
        
        if count <= 0 or type(count) != int:
            return gen_response(400, "message is invalid") 

        #判断数据库是否有该用户或者商品
        try:
            user = User.objects.get(name = username)    
            good = Good.objects.get(id = goodid)
        except Exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "user or good doesn't exist") 
        
        #判断用户是否处于登录状态
        if identify(token) is False:
            return gen_response(444, "user doesn't login now")
        #判断商品是否上架
        if good.available is False:
            return gen_response(406, "the good is off shelf") 

        #判断商品存货、用户余额
        money = user.money
        now_price = good.discount
        if money < now_price * count :
            return gen_response(406, "money is not enough")
        #超过库存
        if count > good.quantities_of_inventory:
            return gen_response(406, "quantity of goods is not enough")
        #更新商品与用户信息
        good.quantities_of_inventory -= count
        good.save()

        number = str(time.time())[0:10]+str(time.time())[11:18]+str(random.randint(10000,99999))+str(goodid)+str(random.randint(10000,99999)) 
        Order.objects.create(user=user, orderid=number, 
            goodid=goodid, name=good.name, count=count, cost = count * now_price , state = 0)
        return gen_response(200, number)
    #禁止使用get来下单
    return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,"please place your order with post")

@csrf_exempt
def pay(request):    
    if request.method == 'POST':
        #是否为json表单
        try:
            json_data = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype")
        
        #判断前端发来的数据是否合法
        try:
            username = json_data['username']
            orderid = json_data['orderid']
            cost = json_data['cost']
            token = json_data['token']

        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid")  
        
        #判断用户是否处于登录状态
        if identify(token) is False:
            return gen_response(HTTPStatus.BAD_REQUEST, "user doesn't login")

        #判断数据库是否有该用户或者商品
        try:
            user = User.objects.get(name = username)    
            order = Order.objects.get(orderid = orderid)
        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "user or order doesn't exist") 

        try:
            good = Good.objects.get(id = order.goodid)
        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "good doesn't exist") 

        cost = order.cost
        if cost < 0:
            return gen_response(400,"cost is wronng")        

        if user.money < cost :
            return gen_response(HTTPStatus.BAD_REQUEST, "money is not enough")
        
        if order.state == 0:
            order.state = 1
            order.save()
        else:
            return gen_response(HTTPStatus.BAD_REQUEST,"your order has been paid")

        user.money -= cost
        user.save()
        good.quantities_sold += order.count
        good.save()


        return gen_response(200,"you have paid successfully")
    return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,
                        "please place your order with post")

@csrf_exempt
def userorder(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))

        except ValueError :
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype") 
        
        try:
            user = json_data['username']
            token = json_data['token']
            
        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid") 

        #判断用户是否处于登录状态
        if identify(token) is False:
            return gen_response(HTTPStatus.BAD_REQUEST, "user doesn't login")

        user = User.objects.get(name=user)
        orderlist = Order.objects.filter(user=user)

        return gen_response(HTTPStatus.OK, [
            dict(orderid= order.orderid,goodid=order.goodid,name=order.name,
                count=order.count,cost=order.cost,date=int(order.pub_date.timestamp()),state=order.state,
                pictures=[picture.file.url for picture in Good.objects.get(id=order.goodid).picture_set.all()])
            for order in orderlist.order_by('-id')
        ])

    return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,"please place your order with post")

@csrf_exempt
def orderlist(request):
    if request.method == 'GET':
        #检验商家身份》待做
        orderlist = Order.objects.all()
        return gen_response(HTTPStatus.OK, [
            dict(user=order.user.name,orderid= order.orderid,goodid=order.goodid,name=order.name,
                count=order.count,cost=order.cost,date=int(order.pub_date.timestamp()),state=order.state,
                pictures=[picture.file.url for picture in Good.objects.get(id=order.goodid).picture_set.all()])
            for order in orderlist.order_by('-id')
        ])

@csrf_exempt
def orderstate(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))

        except ValueError :
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype") 
        
        try:
            orderid = json_data['orderid']
            change = json_data['change']

        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid") 

        try:
            order = Order.objects.get(orderid = orderid)
            merchant = Merchant.objects.get(name = 'merchant')
        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "order doesn't exist")   

        order.state = change
        order.save()

        if order.state == 3 :
            merchant.income += order.cost
            merchant.save()
        
        return gen_response(200,"you have modify the order successfully")

    return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,"please modify an order with post")

@csrf_exempt
def merchantlogin(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))

        except ValueError :
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype") 

        try:
            user = Merchant.objects.get(name = json_data['name']) 
        except Exception :
            return gen_response(400, "merchant doesn't exist")

        if user.password == json_data['password']:
            #创建token
            dic = {
                'exp': time.time() + 23200, #过期时间
                # 'iat': time.time(),#开始时间
                'username': user.name
            }
            s = jwt.encode(dic, settings.SECRET_KEY, algorithm='HS256')
            user.token = s
            user.save()
            return JsonResponse({'code':201, 'data':"login successfully",'token': s , 'income': user.income, 'name':user.name})
                    
        else:
            return gen_response(401, "password is wrong!")
    return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,"please post")

@csrf_exempt
def identify(token):
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms='HS256')
        exp = payload['exp']
        name = payload['username']
    except Exception :
        return False

    if name == 'merchant' and (exp - time.time()) > 0:
        return True
        
    elif (exp - time.time() > 0) and User.objects.filter(name = payload['username']):
        return True
    else:
        return False

@csrf_exempt
def display_money(request):
    
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))

        except ValueError :
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype") 
        
        try:
            r = json_data['role'] 
            name = json_data['name']
            token = json_data['token']
        except Exception :
            return gen_response(400, "unexpected error")

        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms='HS256')
            exp = payload['exp']
        
        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "token is wrong") 

        if (exp - time.time() > 0) :
            if r == 'user' and User.objects.filter(name = name):
                user = User.objects.get(name = name)
                return gen_response(200,user.money)
            if r == 'merchant' and Merchant.objects.filter(name = name):
                merchant = Merchant.objects.get(name = name) 
                return gen_response(200,merchant.income)
        else :
            return gen_response(444,'not login')
            
    return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,"please request with post")

@csrf_exempt
def cancel_order(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))

        except ValueError :
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype") 
        
        try:
            orderid = json_data['orderid']
            token = json_data['token']

        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid") 

        try:
            order = Order.objects.get(orderid = orderid)
            merchant = Merchant.objects.get(name = 'merchant')
        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "order doesn't exist")   
        
        if identify(token):
            user = order.user
            cost = order.cost 
            nowstate = order.state
            count = order.count
            try:
                good = Good.objects.get(id = order.goodid)
            except Exception :
                return gen_response(HTTPStatus.BAD_REQUEST, "good doesn't exist")  

            #刚下单 返库存
            if nowstate == 0:
                good.quantities_of_inventory += count
                good.save()

            #支付未发货/已发货，返库存，返用户钱
            elif nowstate == 1 or nowstate == 2:
                user.money += cost 
                user.save()
                good.quantities_of_inventory += count
                good.quantities_sold -= count
                good.save()

            #已收货   不允许取消订单
            elif nowstate == 3 :
                user.money += cost 
                user.save()
                good.quantities_of_inventory += count
                good.quantities_sold -= count
                good.save()
                merchant.income -= cost
                merchant.save()
            
            order.state = 4
            order.save()
            return gen_response(200,"you have cancel the order successfully")

        else:
            return gen_response(444,"didn't login")
    return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,"please modify an order with post")

@csrf_exempt
def is_login(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))

        except ValueError :
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype") 

        try:
            token = json_data['token']
            user = json_data['user']

        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid") 

        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms='HS256')
            exp = payload['exp']
            m = payload['username']

        except Exception :
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid") 

        if (exp - time.time() > 0) :
            if user == 'user' and User.objects.filter(name = m):
                return gen_response(200,"success")
            if user == 'merchant' and Merchant.objects.filter(name = m):
                return gen_response(200,"success")
        else :
            return gen_response(444,'not login')

    return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,"unexpected error")
    
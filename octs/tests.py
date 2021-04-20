from django.test import TestCase, Client
from django.conf import settings
from .models import User, Coupon ,Order, Merchant, Seckill
from goods.models import Good, Picture
from http import HTTPStatus
import json
import jwt
# Create your tests here.

jsontype="applaction/json" 

class MyTest(TestCase):
    def setUp(self) -> None:
        User.objects.create(name="Alice", password="123456")
        User.objects.create(name="Bob", password="123456")
        Good.objects.create(name="name", desc="description", quantities_of_inventory=3,
                quantities_sold=4, price=17, discount=15, available=True)
        

    def test_add_new_user(self):
        user = {
            'username': "Marry",
            'password': "123456",
        }
        response = self.client.post('/signup/', data=json.dumps(user), content_type=jsontype)
        self.assertJSONEqual(response.content, {'code': 201, 'data': 'sign up successfully'})
        self.assertTrue(User.objects.filter(name="Marry").exists())

    def test_name_or_password_is_none(self):
        user1 = {
            'password': "123456",
        }
        user2 = {
            'username' : "Marry",
        }  
        response1 = self.client.post('/signup/', data = json.dumps(user1) , content_type = jsontype) 
        response2 = self.client.post('/signup/', data = json.dumps(user2) , content_type = jsontype)   
        self.assertJSONEqual(response1.content,{'code':400 ,'data': 'message is invalid'})
        self.assertJSONEqual(response2.content,{'code':400 ,'data': 'message is invalid'})
    
    def test_login(self):
        #正确的用户名和密码
        alice = {
            'username': "Alice",
            'password': "123456",
        }
        #用户存在，密码错误
        bob = {
            'username': 'Bob',
            'password': "456789"
        }
        #用户不存在
        charls = {
            'username':'charls',
            'password': 'asdasd'
        }
        res1 = self.client.post('/login/', data = json.dumps(alice) , content_type = jsontype)
        res2 = self.client.post('/login/', data = json.dumps(bob) , content_type = jsontype)
        res3 = self.client.post('/login/', data = json.dumps(charls) , content_type = jsontype)

        res1 = json.loads(res1.content.decode())
        self.assertEqual(res1['code'],201)
        self.assertJSONEqual(res2.content,{'code':401 ,'data': "password is wrong!"})
        self.assertJSONEqual(res3.content,{'code':400 ,'data': "user doesn't exist"})

    def test_token(self):
        alice = {
            'username': "Alice",
            'password': "123456",
        }
        res = self.client.post('/login/', data = json.dumps(alice) , content_type = jsontype)
        res = json.loads(res.content.decode())
        s = res['token']
        s = jwt.decode(s, settings.SECRET_KEY, algorithms=['HS256'])  
        self.assertTrue(s['exp']>s['iat'])
        self.assertTrue(s['exp']<s['iat']+86401)

    def test_place_order(self):
        test_good = Good.objects.get(name= 'name')
        order = {
            'username': 'Alice',
            'goodid': test_good.id,
            'count' : 1
        }
        wrong_name = {
            'username': 'alice',
            'goodid': test_good.id,
            'count' : 1
        }
        wrong_id = {
            'username': 'Alice',
            'goodid': -1,
            'count' : 1
        }
        wrong_count = {
            'username': 'Alice',
            'goodid': test_good.id,
            'count' : 100
        }
        res = self.client.get('/order/')
        self.assertEqual(json.loads(res.content.decode('utf-8'))['code'],HTTPStatus.METHOD_NOT_ALLOWED)
        self.client.post('/order/',data=json.dumps(wrong_name),content_type = jsontype)
        self.client.post('/order/',data=json.dumps(wrong_id),content_type = jsontype)
        self.client.post('/order/',data=json.dumps(wrong_count),content_type = jsontype)
        res1 = self.client.post('/order/',data=order)
        self.assertEqual(json.loads(res1.content.decode('utf-8'))['code'],HTTPStatus.BAD_REQUEST)
        res2 = self.client.post('/order/',data=json.dumps(order),content_type = jsontype)
        self.assertEqual(json.loads(res2.content.decode('utf-8'))['code'],200)
        alice = User.objects.get(name = 'Alice') 
        test_good = Good.objects.get(name= 'name')
        self.assertEqual(test_good.quantities_of_inventory,2)
        self.assertEqual(test_good.quantities_sold,5)
        
    def place_order(self):
        order = {
            'username': 'Alice',
            'goodid': Good.objects.get(name='name').id,
            'count' : 1
        }
        order1 = {
            'username': 'Alice',
            'goodid': Good.objects.get(name='name').id,
            'count' : 2
        }
        self.client.post('/order/',data=json.dumps(order),content_type = jsontype)
        self.client.post('/order/',data=json.dumps(order1),content_type = jsontype)


    def test_user_order_and_orderlist(self):
        test_good = Good.objects.get(name= 'name')
        
        self.place_order()
        data = {
            'username':'Alice',
        }
        res = self.client.post('/userorder/', data=json.dumps(data),content_type = jsontype)
        for order in json.loads(res.content.decode())['data']:
            self.assertEqual(order['name'],test_good.name)

        res = self.client.get('/orderlist/')
        for order in json.loads(res.content.decode())['data']:
             self.assertEqual(order['user'],"Alice")

    def test_pay(self):
        alice = User.objects.get(name = 'Alice')
        self.place_order()
        order = Order.objects.first()
        data = {
            'username': 'Alice',
            'orderid': order.orderid,
            'cost' : order.cost,
        }
        res = self.client.post('/pay/', data=json.dumps(data),content_type = jsontype)
        res = json.loads(res.content.decode())['code']
        self.assertEqual(res , 200)
        res = self.client.post('/pay/', data=json.dumps(data),content_type = jsontype)
        res = json.loads(res.content.decode())['data']
        self.assertEqual(res , "your order has been paid")

        alice.money = 1
        alice.save()

        self.place_order()
        res = self.client.post('/pay/', data=json.dumps(data),content_type = jsontype)
        self.assertEqual(json.loads(res.content.decode())['data'],"money is not enough")

        self.client.post('/pay/', data=json.dumps({'username':'me'}),content_type = jsontype)
        self.client.post('pay/',json.dumps({'username':'se','orderid':1,'cost':1}),content_type = jsontype)

    def test_order_state(self):
        self.place_order()
        data={
            'orderid' :Order.objects.get(id =1).orderid,
            'change' : 2
        }        
        res = self.client.post('/orderstate/', data=json.dumps(data),content_type = jsontype)
        self.assertEqual(json.loads(res.content.decode())['code'],200)
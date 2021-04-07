from django.test import TestCase, Client
from django.conf import settings
from .models import User, Coupon
from goods.models import Good, Picture
from http import HTTPStatus
import json
import jwt
# Create your tests here.


class MyTest(TestCase):
    def setUp(self) -> None:
        alice = User.objects.create(name="Alice", password="123456")
        bob = User.objects.create(name="Bob", password="123456")
        self.client.post('/upload/', data={
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'now_price': 3.5,
            'available': True,
        })
        Good.objects.create(name="name", desc="description", quantities_of_inventory=3,
                quantities_sold=4, price=17, discount=15, available=True)
        
    def test_add_new_user(self):
        user = {
            'username': "Marry",
            'password': "123456",
        }
        response = self.client.post('/signup/', data=json.dumps(user), content_type="applaction/json")
        self.assertJSONEqual(response.content, {'code': 201, 'data': 'sign up successfully'})
        self.assertTrue(User.objects.filter(name="Marry").exists())

    def test_name_or_password_is_none(self):
        user1 = {
            'password': "123456",
        }
        user2 = {
            'username' : "Marry",
        }  
        response1 = self.client.post('/signup/', data = json.dumps(user1) , content_type = "applaction/json") 
        response2 = self.client.post('/signup/', data = json.dumps(user2) , content_type = "applaction/json")   
        self.assertJSONEqual(response1.content,{'code':400 ,'data': 'message is invalid'})
        self.assertJSONEqual(response2.content,{'code':400 ,'data': 'message is invalid'})
    
    def test_login(self):
        #正确的用户名和密码
        Alice = {
            'username': "Alice",
            'password': "123456",
        }
        #用户存在，密码错误
        Bob = {
            'username': 'Bob',
            'password': "456789"
        }
        #用户不存在
        Charls = {
            'username':'charls',
            'password': 'asdasd'
        }
        res1 = self.client.post('/login/', data = json.dumps(Alice) , content_type = "applaction/json")
        res2 = self.client.post('/login/', data = json.dumps(Bob) , content_type = "applaction/json")
        res3 = self.client.post('/login/', data = json.dumps(Charls) , content_type = "applaction/json")

        res1 = json.loads(res1.content.decode())
        self.assertEqual(res1['code'],201)
        self.assertJSONEqual(res2.content,{'code':401 ,'data': "password is wrong!"})
        self.assertJSONEqual(res3.content,{'code':400 ,'data': "user doesn't exist"})

    def test_token(self):
        Alice = {
            'username': "Alice",
            'password': "123456",
        }
        res = self.client.post('/login/', data = json.dumps(Alice) , content_type = "applaction/json")
        res = json.loads(res.content.decode())
        s = res['token']
        s = jwt.decode(s, settings.SECRET_KEY, algorithms=['HS256'])  
        self.assertTrue(s['exp']>s['iat'])
        self.assertTrue(s['exp']<s['iat']+86401)

    def test_place_order(self):
        alice = User.objects.get(name = 'Alice')
        test_good = Good.objects.get(name= 'name')
        print(test_good.id,test_good.desc)
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
        res1 = self.client.post('/order/',data=order)
        self.assertEqual(json.loads(res1.content.decode('utf-8'))['code'],HTTPStatus.BAD_REQUEST)
        res2 = self.client.post('/order/',data=json.dumps(order),content_type = "applaction/json")
        self.assertEqual(json.loads(res2.content.decode('utf-8'))['code'],200)
        alice = User.objects.get(name = 'Alice') 
        test_good = Good.objects.get(name= 'name')
        self.assertEqual(test_good.quantities_of_inventory,2)
        self.assertEqual(test_good.quantities_sold,5)
        self.assertEqual(alice.money, 9985)
        

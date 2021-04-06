from django.test import TestCase, Client
from .models import User
import json
import jwt
# Create your tests here.


class MyTest(TestCase):
    def setUp(self) -> None:
        self.data = 1
        alice = User.objects.create(name="Alice", password="123456")
        bob = User.objects.create(name="Bob", password="123456")

        
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
        pass
         
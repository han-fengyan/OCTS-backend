import json
from http import HTTPStatus
from django.test import TestCase, Client
from .models import Good

# Create your tests here.


class GoodTest(TestCase):
    def setUp(self) -> None:
        self.data = 1
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        response = self.client.post('/upload/', data=json.dumps({
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'new_price': 3.5,
            'picture': '/commodities/',
            'available': False,
        }, ensure_ascii=False), content_type="application/json")
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK

    def test_fslls(self):
        self.assertTrue(self.data == 1)

    def test_default_available_upload(self):
        response = self.client.post('/upload/', data=json.dumps({
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'new_price': 3.5,
            'picture': '/commodities/',
        }, ensure_ascii=False), content_type="application/json")
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK

    def test_binary_pic_upload(self):
        with open('commodities/1.jpg') as pic:
            response = self.client.post('/upload/', data=json.dumps(
                dict(title='江山图', introduction='是一幅名贵的画', store=3, sell=0,
                     old_price=199.9, new_price=3.5, picture=pic), ensure_ascii=False),
                content_type="application/json")
            assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK

    def test_get_upload(self):
        response = self.client.get('/upload/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED


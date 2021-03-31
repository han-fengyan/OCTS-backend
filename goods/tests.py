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
        # test invalid json
        response = self.client.post('/upload/', {
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'new_price': 3.5,
            'pictures': '/commodities/',
        }, content_type="application/json")
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.BAD_REQUEST

    def test_get_upload(self):
        response = self.client.get('/upload/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED

    def test_get_list(self):
        response = self.client.get('/list/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/list/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED

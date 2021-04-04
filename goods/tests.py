import json
from http import HTTPStatus
from django.test import TestCase, Client
from .models import Good


# Create your tests here.


class GoodTest(TestCase):  # pragma: no cover
    def setUp(self) -> None:
        self.data = 1
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        # response = self.client.post('/upload/', data=json.dumps({
        #     'title': '江山图',
        #     'introduction': '是一幅名贵的画',
        #     'store': 3,
        #     'sell': 0,
        #     'old_price': 199.9,
        #     'new_price': 3.5,
        #     'picture': '/commodities/',
        #     'available': False,
        # }, ensure_ascii=False), content_type="application/json")

    def test_upload(self):
        response = self.client.post('/upload/', data={
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'now_price': 3.5,
            'available': False,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        # f = open("../pictures/1.png", 'rb')
        # response = self.client.post('/upload/', data={
        #     'title': '江山图',
        #     'introduction': '是一幅名贵的画',
        #     'store': 3,
        #     'sell': 0,
        #     'old_price': 199.9,
        #     'now_price': 3.5,
        #     'available': False,
        #     'pictures': f,
        # })
        # assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        # f.close()

    def test_default_available_upload(self):
        response = self.client.post('/upload/', data={
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'now_price': 3.5,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        # test wrong type of load
        response = self.client.post('/upload/', data=json.dumps({
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'now_price': 3.5,
        }, ensure_ascii=False), content_type="application/json")
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.BAD_REQUEST

    def test_get_upload(self):
        response = self.client.get('/upload/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED

    def test_get_list(self):
        response = self.client.get('/list/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/list/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED

    def test_modify(self):
        self.client.post('/upload/', data={
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'now_price': 3.5,
            'available': True,
        })
        response = self.client.post('/status/', data=json.dumps({
            'id': 1
        }), content_type="application/json")
        # assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/status/', {
            'id1': 1000
        }, content_type="application/json")
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.NOT_ACCEPTABLE
        response = self.client.post('/status/', {
            'id': 1000
        }, content_type="application/json")
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE
        response = self.client.post('/status/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.BAD_REQUEST
        response = self.client.get('/status/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED

    def test_list(self):
        self.client.get('/list/')

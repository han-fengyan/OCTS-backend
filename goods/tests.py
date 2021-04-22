import json
from http import HTTPStatus
from django.test import TestCase, Client
from .models import Good, Favourite
from octs.models import User


# Create your tests here.
#NOSONAR

class GoodTest(TestCase):  # pragma: no cover
    def setUp(self) -> None:
        self.data = 1
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')

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
        user = User(name='2', password='12345')
        user.save()
        response = self.client.post('/products/', data=json.dumps({
            'username': '1'
        }, ensure_ascii=False), content_type="application/json")
        response = self.client.post('/products/', data=json.dumps({
            'username': '2'
        }, ensure_ascii=False), content_type="application/json")
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.get('/products/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.delete('/products/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED

    def test_shelf(self):
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

    def test_detail(self):
        self.client.post('/upload/', data={
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'now_price': 3.5,
            'available': True,
        })
        self.client.get('/details/1')
        self.client.get('/details/2')
        self.client.get('/details/5')

    def test_modify(self):
        product = Good(name='江山图',
                       desc='是一幅名贵的画',
                       quantities_of_inventory=3,
                       quantities_sold=0,
                       price=199.9,
                       discount=3.5,
                       available=False)
        product.save()
        self.client.get('/modify/')
        self.client.post('/modify/', data={
            'id': product.id,
            'title': '画',
            'introduction': '是名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 203.9,
            'now_price': 4.5,
            'available': True,
        })
        self.client.post('/modify/', data={
            'id': product.id,
            'title': '画',
            'introduction': '是名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 203.9,
            'now_price': 4.5,
            'available': True,
            'delete': 'https://octs-backend-justdebugit.app.secoder.net/pic/pictures/1.jpg',
        })
        self.client.post('/modify/', data={
            'id': product.id,
            'introduction': '是名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 203.9,
            'now_price': 4.5,
            'available': True,
        })
        self.client.post('/modify/', data={
            'id': product.id+1,
            'introduction': '是名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 203.9,
            'now_price': 4.5,
            'available': True,
        })

    def test_search(self):
        response = self.client.get("/search/", data={
            'keyword': '江山'
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.get("/searchcanary/", data={
            'keyword': '江山'
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post("/search/")
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED
        response = self.client.post("/searchcanary/")
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED

    def test_my_favourite(self):
        user = User(name='wer', password='12345')
        user.save()
        user2 = User(name='wer2', password='12345')
        user2.save()
        product = Good(name='江山图',
                       desc='是一幅名贵的画',
                       quantities_of_inventory=3,
                       quantities_sold=0,
                       price=199.9,
                       discount=3.5,
                       available=False)
        product.save()
        fav = Favourite(user=user)
        fav.save()
        fav.goods.add(product)
        response = self.client.get('/myfavourites/', data={
            'username': 'wer'
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.get('/myfavourites/', data={
            'username': 'wer2'
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/favourite/', data=json.dumps({
            'username': 'wer',
            'id': product.id,
        }, ensure_ascii=False), content_type='application/json')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/favourite/', data=json.dumps({
            'username': 'wer2',
            'id': product.id,
        }, ensure_ascii=False), content_type='application/json')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/favourite/', data=json.dumps({
            'username': 'wer3',
            'id': product.id,
        }, ensure_ascii=False), content_type='application/json')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.BAD_REQUEST
        response = self.client.post('/favourite/', data=json.dumps({
            'username': 'wer',
            'id': product.id+1,
        }, ensure_ascii=False), content_type='application/json')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE
        response = self.client.get('/favourite/', data={
            'username': 'wer',
            'id': product.id+1,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED

    def test_draft(self):
        response = self.client.post('/save/', data={
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'now_price': 3.5,
            'available': False,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/save/', data={
            'title': '江山图',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'now_price': 3.5,
            'available': False,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/save/', data={
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'sell': 0,
            'old_price': 199.9,
            'now_price': 3.5,
            'available': False,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/save/', data={
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'old_price': 199.9,
            'now_price': 3.5,
            'available': False,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/save/', data={
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'now_price': 3.5,
            'available': False,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/save/', data={
            'title': '江山图',
            'introduction': '是一幅名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 199.9,
            'available': False,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.get('/save/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED
        response = self.client.get('/drafts/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK

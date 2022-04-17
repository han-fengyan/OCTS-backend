import json
import jwt
import time
from http import HTTPStatus

from django.test import TestCase, Client
from django.conf import settings

from octs.models import User, Merchant, Order
from .models import Good, Favourite, Draft


# Create your tests here.
# NOSONAR

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
            'id': product.id + 1,
            'introduction': '是名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 203.9,
            'now_price': 4.5,
            'available': True,
        })

    def test_search(self):
        response = self.client.get("/search/", data={
            'keyword': '江山',
            'type': 0
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post("/search/")
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED
        for index in range(12):
            self.client.get("/search/", data={
                'keyword': '江山',
                'type': index,
            })

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
            'id': product.id + 1,
        }, ensure_ascii=False), content_type='application/json')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE
        response = self.client.get('/favourite/', data={
            'username': 'wer',
            'id': product.id + 1,
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

    def test_commit(self):
        draft = Draft(name='江山图',
                      desc='是一幅名贵的画',
                      quantities_of_inventory=3,
                      quantities_sold=0,
                      price=199.9,
                      discount=3.5,
                      available=False)
        draft.save()
        response = self.client.get('/commit/')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.METHOD_NOT_ALLOWED
        self.client.post('/commit/', data={
            'id': draft.id,
            'title': '画',
            'introduction': '是名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 203.9,
            'now_price': 4.5,
            'available': True,
            'delete': 'https://octs-backend-justdebugit.app.secoder.net/pic/pictures/1.jpg\nhttps://octs-backend'
                      '-justdebugit.app.secoder.net/pic/pictures/1.jpg',
        })
        draft = Draft(name='江山图',
                      desc='是一幅名贵的画',
                      quantities_of_inventory=3,
                      quantities_sold=0,
                      price=199.9,
                      discount=3.5,
                      available=False)
        draft.save()
        response = self.client.post('/commit/', data={
            'id': draft.id,
            'introduction': '是名贵的画',
            'store': 3,
            'sell': 0,
            'old_price': 203.9,
            'now_price': 4.5,
            'available': True,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.BAD_REQUEST
        response = self.client.post('/commit/', data={
            'id': draft.id + 1,
        })

    def test_edit_draft(self):
        draft = Draft(name='江山图234',
                      desc='是一幅名贵的画2345',
                      quantities_of_inventory=3,
                      quantities_sold=0,
                      price=199.9,
                      discount=3.5,
                      available=False)
        draft.save()
        self.client.get('/drafedit/')
        response = self.client.post('/draftedit/', data={
            'id': draft.id,
            'title': "hhhhh"
        })

    def test_comment(self):
        product = Good(name='江山图123',
                       desc='是一幅名贵的画234',
                       quantities_of_inventory=3,
                       quantities_sold=0,
                       price=199.9,
                       discount=3.5,
                       available=True)
        product.save()
        user = {
            'username': "Marry",
            'password': "123456",
        }
        self.client.post('/signup/', data=json.dumps(user), content_type="application/json")
        order = Order(name='Marry', user_id=1, goodid=product.id)
        order.save()
        dic = {
            'exp': time.time() + 23200,  # 过期时间
            'iat': time.time(),  # 开始时间
            'username': 'Marry'
        }
        s = jwt.encode(dic, settings.SECRET_KEY, algorithm='HS256')
        # 正常测试
        response = self.client.post('/comment/', {
            'username': 'Marry',
            'orderid': order.orderid,
            'comment': '针不戳',
            'token': s,
            'rating': 5,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        # 测试错误token
        response = self.client.post('/comment/', {
            'username': 'Marry',
            'orderid': order.orderid,
            'comment': '针不戳',
            'token': '  ',
            'rating': 5,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.SERVICE_UNAVAILABLE
        response = self.client.post('/comment/', {
            'username': 'Marry',
            'orderid': order.orderid,
            'comment': '针不戳',
            'token': s,
            'rating': 10,
        })
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.FORBIDDEN

    def test_tags(self):
        # test add new tag
        dic = {
            'exp': time.time() + 23200,  # 过期时间
            'iat': time.time(),  # 开始时间
            'username': 'merchant'
        }
        s = jwt.encode(dic, settings.SECRET_KEY, algorithm='HS256')
        response = self.client.post('/newtag/', data={
            'name': '新标签',
            'token': s,
        }, content_type='application/json')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK
        response = self.client.post('/newtag/', data={
            'name': '新标签',
            'token': 123,
        }, content_type='application/json')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.SERVICE_UNAVAILABLE
        # test attach tag
        product = Good(name='江山图234',
                       desc='是一幅名贵的画2346',
                       quantities_of_inventory=3,
                       quantities_sold=0,
                       price=199.9,
                       discount=3.5,
                       available=True)
        product.save()
        response = self.client.post('/addtag/', data={
            'tag': '新标签',
            'id': product.id,
        }, content_type='application/json')
        assert json.loads(response.content.decode('utf-8'))['code'] == HTTPStatus.OK


def test_pp(self):
    self.client.post('/pp/',data=json.dumps({
        'id':1,
        'price':15,
        'date':11,
    }),content_type='application/json')
    pass
from django.http import JsonResponse, HttpResponse
from http import HTTPStatus
from .models import Good
import json


# Create your views here.

def gen_response(code, mes):
    return JsonResponse({
        'code': code,
        'data': mes,
    }, status=code, content_type='application/json')


def add(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))
        except ValueError as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype")
        # 判断前端发来的数据是否合法
        try:
            name = json_data['title']
            description = json_data['introduction']
            quantities_of_inventory = json_data['store']
            quantities_sold = json_data['sell']
            ori_price = json_data['old_price']
            cur_price = json_data['new_price']
            pic_url = json_data['picture']
            print(pic_url)
            if len(name) > 100:
                return gen_response(HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                                    "name too long")
            if len(description) > 1000:
                return gen_response(HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                                    "description too long")

        except KeyError as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "miss key message")
        except Exception as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid")
        try:
            available = json_data['available']
        except KeyError as exception:
            available = True
        good = Good(name=name, desc=description, quantities_of_inventory=quantities_of_inventory,
                     quantities_sold=quantities_sold, price=ori_price, discount=cur_price,
                     pictures_link=pic_url, available=available)
        good.save()
        return gen_response(HTTPStatus.OK, "product no%d added" % good.id)
    else:
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "please post your new product")
    # return HttpResponse("<html><body>register new commodities</body></html>")


def products_list(request):
    if request.method == 'GET':
        products = Goods.objects.filter(available=True)
    else:
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "please get all of our products")


def all_products(request):
    pass


def detail(request, id):
    return HttpResponse("<html><body>Get for commodities detail %d</body></html>" % id)


def modify(request, id):
    return HttpResponse("<html><body>modifying product No.%d</body></html>" % id)

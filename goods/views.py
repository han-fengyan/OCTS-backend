from django.http import JsonResponse, HttpResponse
from http import HTTPStatus
from .models import Good, Picture
import json


# Create your views here.

def gen_response(code, mes):
    return JsonResponse({
        'code': code,
        'data': mes,
    }, status=code, content_type='application/json')


def add_product(request):
    if request.method != 'POST':
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,
                            "please add your product with post")
    try:  # 从表单中拿出数据
        name = request.POST["title"]
        description = request.POST["introduction"]
        quantities_of_inventory = request.POST["store"]
        quantities_sold = request.POST['sell']
        ori_price = request.POST['old_price']
        cur_price = request.POST['now_price']
    except KeyError as exception:
        return gen_response(HTTPStatus.BAD_REQUEST, "miss key message")
    except Exception as exception:
        return gen_response(HTTPStatus.BAD_REQUEST, "message is invalid")
    try:  # 判断商品是否上架，默认上架
        available = True if request.POST['available'] == "true" else False
    except KeyError as exception:
        available = True

    good = Good(name=name, desc=description, quantities_of_inventory=quantities_of_inventory,
                quantities_sold=quantities_sold, price=ori_price, discount=cur_price,
                available=available)
    # good = Good(name="name", desc="description", quantities_of_inventory=3,
    #             quantities_sold=4, price=17.99, discount=15.99,
    #             available=True)
    good.save()
    try:
        pictures = request.FILES.getlist('pictures')
        for picture in pictures:
            pic = Picture(file=picture, good=good)
            pic.save()
    except KeyError as exception:
        pass
    return gen_response(HTTPStatus.OK, "product no%d added" % good.id)


def products_list(request):
    """
    return products_list with all available products to consumers
    """
    if request.method == 'GET':
        products = Good.objects.filter(available=True)
        jsons_list = [
            dict(id=product.id, title=product.name, introduction=product.desc,
                 old_price=product.price, now_price=product.discount, sell=product.quantities_sold,
                 store=product.quantities_of_inventory,
                 pictures=[picture.file.url for picture in product.picture_set.all()])
            for product in products
        ]
        return gen_response(HTTPStatus.OK, jsons_list)
    else:
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "please get all of our products")


def all_products(request):
    if request.method == 'GET':
        json_list = [
            dict(id=product.id, title=product.name, introduction=product.desc, old_price=product.price,
                 now_price=product.discount, sell=product.quantities_sold,
                 store=product.quantities_of_inventory, available=product.available,
                 pictures=[picture.file.url for picture in product.picture_set.all()])
            for product in Good.objects.all()
        ]
        return gen_response(HTTPStatus.OK, json_list)
    else:
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "please get all of our products")


def detail(request, id):
    try:
        product = Good.objects.get(id=id)
        return gen_response(HTTPStatus.OK, dict(
            id=product.id, title=product.name, introduction=product.desc,
            old_price=product.price, now_price=product.discount,
            sell=product.quantities_sold,
            store=product.quantities_of_inventory, available=product.available,
            pictures=[picture.file.url for picture in product.picture_set.all()]))
    except Exception as e:
        return gen_response(HTTPStatus.NOT_FOUND, "product not found")


def modify(request):
    if request.method != 'POST':
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, '')
    try:
        id = request.POST['id']
        product = Good.objects.get(id=id)
        # product.delete()
    except Exception as e:
        return gen_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE, '')

    try:  # 从表单中拿出数据
        name = request.POST["title"]
        description = request.POST["introduction"]
        quantities_of_inventory = request.POST["store"]
        quantities_sold = request.POST['sell']
        ori_price = request.POST['old_price']
        cur_price = request.POST['now_price']
        available = request.POST['available']
    except KeyError:
        return gen_response(HTTPStatus.BAD_REQUEST, "miss key message")

    product.name = name
    product.desc = description
    product.quantities_of_inventory = quantities_of_inventory
    product.price = ori_price
    product.discount = cur_price
    product.available = True if available == "true" else False
    product.save()

    try:
        deleted_pictures = request.POST['delete']
        pictures = deleted_pictures.split('\n')[:-1]
        print(pictures)
        # https://octs-backend-justdebugit.app.secoder.net/pic/pictures/1.jpg
        for picture in pictures:
            url = picture[48:]
            try:
                picture = Picture.objects.get(file=url)
                picture.delete()
            except Exception:
                pass
    except KeyError:
        pass

    try:
        pictures = request.FILES.getlist('pictures')
        for picture in pictures:
            pic = Picture(file=picture, good=product)
            pic.save()
    except KeyError:
        pass
    return gen_response(HTTPStatus.OK, "successfully modify")


def on_off_shelf(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))
        except ValueError as exception:
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype")

        products = Good.objects.all()
        # check id range
        try:
            id = json_data['id']
        except KeyError as exception:
            return gen_response(HTTPStatus.NOT_ACCEPTABLE, 'pleas specify id')
        # modify availability
        try:
            product = products.get(id=id)
            product.available = not product.available
            product.save()
            return gen_response(HTTPStatus.OK, "on" if product.available else "off")
        except Exception as exception:
            return gen_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE, 'no product with id %d' % id)

    else:
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "please change your product's settings with post")

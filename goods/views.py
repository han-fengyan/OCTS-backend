from django.http import JsonResponse, HttpResponse
from http import HTTPStatus
from .models import Good, Picture, Category, Keyword, Favourite, Draft
from octs.models import User
import json
import jieba


# Create your views here.

def gen_response(code, mes):
    return JsonResponse({
        'code': code,
        'data': mes,
    }, status=code, content_type='application/json')


def products_lists_response(products, favourites=False, user=None):
    if products is not None:
        if favourites:
            if user is not None:
                favourite = user.favourite.goods.all()
                return gen_response(HTTPStatus.OK, [
                    dict(id=product.id, title=product.name, introduction=product.desc,
                         old_price=product.price,
                         now_price=product.discount, sell=product.quantities_sold,
                         store=product.quantities_of_inventory, available=product.available,
                         pictures=[picture.file.url for picture in product.picture_set.all()],
                         liked=favourite is not None and product in favourite)
                    for product in products
                ])
            else:
                return gen_response(HTTPStatus.OK, [
                    dict(id=product.id, title=product.name, introduction=product.desc,
                         old_price=product.price,
                         now_price=product.discount, sell=product.quantities_sold,
                         store=product.quantities_of_inventory, available=product.available,
                         pictures=[picture.file.url for picture in product.picture_set.all()],
                         liked=True)
                    for product in products
                ])
        else:
            return gen_response(HTTPStatus.OK, [
                dict(id=product.id, title=product.name, introduction=product.desc, old_price=product.price,
                     now_price=product.discount, sell=product.quantities_sold,
                     store=product.quantities_of_inventory, available=product.available,
                     pictures=[picture.file.url for picture in product.picture_set.all()], )
                for product in products
            ])
    else:
        return gen_response(HTTPStatus.OK, [])


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
    except KeyError:
        return gen_response(HTTPStatus.BAD_REQUEST, "miss key message")

    try:  # 判断商品是否上架，默认上架
        available = True if request.POST['available'] == "true" else False
    except KeyError:
        available = True

    good = Good(name=name, desc=description, quantities_of_inventory=quantities_of_inventory,
                quantities_sold=quantities_sold, price=ori_price, discount=cur_price,
                available=available)
    good.save()
    try:
        pictures = request.FILES.getlist('pictures')
        for picture in pictures:
            pic = Picture(file=picture, good=good)
            pic.save()
    except KeyError:
        pass
    return gen_response(HTTPStatus.OK, "product no%d added" % good.id)


def collect_favourite(request):
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))
        try:
            user = User.objects.get(name=json_data['username'])
        except:
            return gen_response(HTTPStatus.BAD_REQUEST, "")
        try:
            favourites = user.favourite
        except:
            favourites = Favourite(user=user)
            favourites.save()
        try:
            product_id = json_data['id']
            product = Good.objects.get(id=product_id)
        except:
            return gen_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE, "")
        if product in favourites.goods.all():
            favourites.goods.remove(product)
        else:
            favourites.goods.add(product)
        return gen_response(HTTPStatus.OK, "successfully liked product")
    else:
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "please post your favourites")


def my_favourites(request):
    if request.method != 'GET':
        pass
    username = request.GET['username']
    user = User.objects.get(name=username)
    try:
        product_list = user.favourite.goods.all()
        return products_lists_response(product_list, True)
    except Exception:
        return products_lists_response(None)


def products_list(request):
    """
    return products_list with all available products to consumers
    """
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))
        favourites = None
        try:
            user = User.objects.get(name=json_data['username'])
            favourites = user.favourite.goods.all()
        except Exception as e:
            pass
        products = Good.objects.filter(available=True)
        jsons_list = [
            dict(id=product.id, title=product.name, introduction=product.desc,
                 old_price=product.price, now_price=product.discount, sell=product.quantities_sold,
                 store=product.quantities_of_inventory,
                 pictures=[picture.file.url for picture in product.picture_set.all()],
                 liked=favourites is not None and product in favourites
                 )
            for product in products
        ]
        return gen_response(HTTPStatus.OK, jsons_list)
    elif request.method == 'GET':
        products = Good.objects.filter(available=True)
        jsons_list = [
            dict(id=product.id, title=product.name, introduction=product.desc,
                 old_price=product.price, now_price=product.discount, sell=product.quantities_sold,
                 store=product.quantities_of_inventory,
                 pictures=[picture.file.url for picture in product.picture_set.all()],
                 )
            for product in products
        ]
        return gen_response(HTTPStatus.OK, jsons_list)
    else:
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "used wrong methods")


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
    except Exception:
        return gen_response(HTTPStatus.NOT_FOUND, "product not found")


def modify(request):
    if request.method != 'POST':
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, '')
    try:
        product_i = request.POST['id']
        product = Good.objects.get(id=product_i)
        # product.delete()
    except Exception:
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
        for picture in pictures:
            url = picture[53:]
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
        except ValueError:
            return gen_response(HTTPStatus.BAD_REQUEST, "wrong json datatype")

        products = Good.objects.all()
        # check id range
        try:
            id = json_data['id']
        except KeyError:
            return gen_response(HTTPStatus.NOT_ACCEPTABLE, 'pleas specify id')
        # modify availability
        try:
            product = products.get(id=id)
            product.available = not product.available
            product.save()
            return gen_response(HTTPStatus.OK, "on" if product.available else "off")
        except Exception:
            return gen_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE, 'no product with id %d' % id)

    else:
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "please change your product's settings with post")


def search(request):
    if request.method != 'GET':
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "")
    keyword = request.GET['keyword']
    products = Good.objects.filter(name__contains=keyword)
    try:
        user = User.objects.get(name=request.GET['username'])
        return products_lists_response(products=products, favourites=True, user=user)
    except:
        return products_lists_response(products)


def advanced_search(request):
    if request.method != 'GET':
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "")
    keyword = request.GET['keyword']
    key_list = jieba.cut_for_search(keyword)
    for key in key_list:
        pass
    products = Good.objects.filter(name__contains=keyword)
    return products_lists_response(products)


def add_draft(request):
    if request.method != 'POST':
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED,
                            "please save your draft with post")
    draft = Draft()
    print(request.POST, )
    try:  # 从表单中拿出数据
        name = request.POST["title"]
        draft.name = name
    except KeyError:
        pass
    try:
        description = request.POST["introduction"]
        draft.desc = description
    except KeyError:
        pass
    try:
        quantities_of_inventory = request.POST["store"]
        if quantities_of_inventory != '':
            draft.quantities_of_inventory = quantities_of_inventory
    except KeyError:
        pass
    try:
        quantities_sold = request.POST['sell']
        if quantities_sold != '':
            draft.quantities_sold = quantities_sold
    except KeyError:
        pass
    try:
        ori_price = request.POST['old_price']
        if ori_price != '':
            draft.price = ori_price
    except KeyError:
        pass
    try:
        cur_price = request.POST['now_price']
        if cur_price != '':
            draft.discount = cur_price
    except KeyError:
        pass
    draft.save()
    try:
        pictures = request.FILES.getlist('pictures')
        for picture in pictures:
            pic = Picture(file=picture, draft=draft)
            pic.save()
    except KeyError:
        pass
    return gen_response(HTTPStatus.OK, "draft successfully saved")


def all_drafts(request):
    json_list = [
        dict(id=draft.id, title=draft.name, introduction=draft.desc, old_price=draft.price,
             now_price=draft.discount, store=draft.quantities_of_inventory,
             pictures=[picture.file.url for picture in draft.picture_set.all()])
        for draft in Draft.objects.all()
    ]
    return gen_response(HTTPStatus.OK, json_list)


def commit_draft(request):
    if request.method != 'POST':
        return gen_response(HTTPStatus.METHOD_NOT_ALLOWED, "")
    try:
        draft_id = request.POST['id']
        draft = Draft.objects.get(id=draft_id)
        # product.delete()
    except Exception:
        return gen_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE, '')

    try:  # 从表单中拿出数据
        name = request.POST["title"]
        description = request.POST["introduction"]
        quantities_of_inventory = request.POST["store"]
        quantities_sold = request.POST['sell']
        ori_price = request.POST['old_price']
        cur_price = request.POST['now_price']
    except KeyError:
        return gen_response(HTTPStatus.BAD_REQUEST, "miss key message")

    available = True

    good = Good(name=name, desc=description, quantities_of_inventory=quantities_of_inventory,
                quantities_sold=quantities_sold, price=ori_price, discount=cur_price,
                available=available)
    good.save()

    try:
        deleted_pictures = request.POST['delete']
        pictures = deleted_pictures.split('\n')[:-1]
        for picture in pictures:
            url = picture[53:]
            try:
                picture = Picture.objects.get(file=url)
                picture.delete()
            except Exception:
                pass
    except KeyError:
        pass
    for picture in draft.picture_set.all():
        picture.draft = None
        picture.good = good
        picture.save()

    try:
        pictures = request.FILES.getlist('pictures')
        for picture in pictures:
            pic = Picture(file=picture, good=good)
            pic.save()
    except KeyError:
        pass

    draft.delete()
    return HttpResponse(HTTPStatus.OK, "")


def edit_draft(request):
    pass

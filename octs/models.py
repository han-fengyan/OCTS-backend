from django.db import models
from django.forms import ModelForm

# Create your models here.

class User(models.Model):
    name = models.CharField(unique=True, max_length=20)
    register_date = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length = 500)
    money = models.FloatField(default=10000)
    token = models.CharField(max_length =500,default=None,null=True)

    def __str__(self):
        return self.name

class Coupon(models.Model):
    name = models.CharField(max_length=20,default="优惠券")
    describe = models.CharField(max_length=200,default="可以对任意商品使用")
    dicount = models.FloatField(default=0)
    decrease = models.FloatField(default=0)
    usage = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add = True)
    end = models.DateTimeField(auto_now_add = True)
       

class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    orderid = models.CharField(max_length = 30)
    goodid = models.IntegerField(default = 0)
    name = models.CharField(max_length = 100)
    count = models.IntegerField(default = 0)
    cost = models.FloatField(default=10)
    pub_date = models.DateTimeField(auto_now_add = True)
    state = models.IntegerField(default = 0) #状态码： 0：未支付；1：已支付；2:已发货; 3：已收货

#商家
class Merchant(models.Model):
    name = models.CharField(unique=True, max_length=20) 
    photo = models.ImageField(upload_to='pictures/', blank=True, null=True)
    password = models.CharField(max_length=200)
    token = models.CharField(max_length =500,default=None,null=True)
    income = models.FloatField(default=0)


#秒杀活动
class Seckill(models.Model):
    name = models.CharField(max_length=50)
    descripe = models.CharField(max_length=500, default=None)
    start = models.DateTimeField()
    end = models.DateTimeField()
    status =  models.IntegerField(default=0)
    

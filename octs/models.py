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
    pass    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    orderid = models.CharField(max_length = 30)
    goodid = models.IntegerField(default = 0)
    name = models.CharField(max_length = 100)
    count = models.IntegerField(default = 0)
    cost = models.FloatField(default=10)
    pub_date = models.DateTimeField(auto_now_add = True)
    state = models.IntegerField(default = 0) #状态码： 0：未支付；1：已支付；2:已发货; 3：已收获
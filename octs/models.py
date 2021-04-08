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

class UserOrder(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    orderid = models.CharField(max_length = 30)
    name = models.CharField(max_length = 100)
    count = models.IntegerField(default = 0)
    pub_date = models.DateTimeField(auto_now_add = True)
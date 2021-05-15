from django.db import models
from octs.models import Seckill, User


# Create your models here.


class Good(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000)
    available = models.BooleanField(default=True)
    quantities_of_inventory = models.IntegerField()
    quantities_sold = models.IntegerField(default=0)
    price = models.FloatField()
    discount = models.FloatField(default=0)

    average_rating = models.FloatField(default=5)

    def __str__(self):
        return self.name


class Draft(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    desc = models.CharField(max_length=1000, null=True, blank=True)
    available = models.BooleanField(default=True, null=True, blank=True)
    quantities_of_inventory = models.IntegerField(null=True, blank=True)
    quantities_sold = models.IntegerField(default=0, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    discount = models.FloatField(default=0, null=True, blank=True)


class Picture(models.Model):
    file = models.ImageField(upload_to='pictures/', blank=True, null=True)
    good = models.ForeignKey(Good, on_delete=models.CASCADE, null=True, blank=True)
    draft = models.ForeignKey(Draft, on_delete=models.CASCADE, null=True, blank=True)


class Tag(models.Model):
    name = models.CharField(max_length=50)
    products = models.ManyToManyField(Good)


class Keyword(models.Model):
    keyword = models.CharField(max_length=100)
    products = models.ManyToManyField(Good)


class Favourite(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    goods = models.ManyToManyField(Good)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    good = models.ForeignKey(Good, on_delete=models.CASCADE)
    rate = models.IntegerField(default=5)
    comment = models.CharField(max_length=500)


class SalePromotion(models.Model):
    good = models.OneToOneField(Good, on_delete=models.CASCADE)
    end_time = models.CharField(max_length=500)
    discount_price = models.FloatField()

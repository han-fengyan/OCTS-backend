from django.db import models
from octs.models import Seckill
# Create your models here.


class Good(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000)
    available = models.BooleanField(default=True)
    quantities_of_inventory = models.IntegerField()
    quantities_sold = models.IntegerField(default=0)
    price = models.FloatField()
    discount = models.FloatField(default=0)
    seckill  = models.ForeignKey(Seckill, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.name


class Picture(models.Model):
    file = models.ImageField(upload_to='pictures/', blank=True, null=True)
    good = models.ForeignKey(Good, on_delete=models.CASCADE)

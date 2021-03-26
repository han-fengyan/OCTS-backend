from django.db import models

# Create your models here.


class Goods(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000)
    available = models.BooleanField(default=True)
    quantities_of_inventory = models.IntegerField()
    quantities_sold = models.IntegerField(default=0)
    price = models.FloatField()
    discount = models.FloatField(default=0)
    pictures_link = models.ImageField(upload_to='commodities/')

    def __str__(self):
        return self.name

from django.db import models

# Create your models here.


class Good(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000)
    available = models.BooleanField(default=True)
    quantities_of_inventory = models.IntegerField()
    quantities_sold = models.IntegerField(default=0)
    price = models.FloatField()
    discount = models.FloatField(default=0)
    pictures = models.ImageField(upload_to='commodities/')
    # pictures_url = models.CharField(max_length=650)

    def __str__(self):
        return self.name

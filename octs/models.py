from django.contrib import admin
from django.forms import ModelForm
# Create your models here.

class User(models.Model):
    name = models.CharField(unique=True, max_length=20)
    register_date = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length = 500)
    
    def __str__(self):
        return self.name
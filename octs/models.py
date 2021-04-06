from django.db import models
from django.forms import ModelForm
# Create your models here.

class User(models.Model):
    name = models.CharField(unique=True, max_length=20)
    register_date = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length = 500)
    money = models.FloatField(default=10000)
    token = models.CharField(max_length =500,default=None)

    def __str__(self):
        return self.name

    @property
    def token(self):
        return self._generate_jwt_token()
 
    def _generate_jwt_token(self):
        token = jwt.encode({
            'exp': datetime.utcnow() + timedelta(days=1),
            'init_time': datetime.utcnow(),
            'username': self.name
        }, settings.SECRET_KEY, algorithm='HS256')
 
        return token.decode('utf-8')


class Coupon(models.Model):
    pass
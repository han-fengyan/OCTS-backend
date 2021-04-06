from django.db import models
from django.forms import ModelForm
import jwt

# Create your models here.

# class DateEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj,datetime.datetime):
#             return obj.strftime("%Y-%m-%d %H:%M:%S")
#         else:
#             return json.JSONEncoder.default(self,obj)

class User(models.Model):
    name = models.CharField(unique=True, max_length=20)
    register_date = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length = 500)
    money = models.FloatField(default=10000)
    token = models.CharField(max_length =500,default=None,null=True)

    def __str__(self):
        return self.name

    # # @property
    # def get_token(self):
    #     return self._generate_jwt_token()
 
    # def _generate_jwt_token(self):
    #     dic = {
    #         'exp': datetime.utcnow() + timedelta(days=1), #过期时间
    #         'iat': datetime.utcnow(),#开始时间
    #         'username': self.name
    #     }
    #     token = jwt.encode(dic, settings.SECRET_KEY, algorithm='HS256')
    #     return token.decode('utf-8')


class Coupon(models.Model):
    pass
from django.contrib import admin
import sys
from .models import User, Coupon, Order, Merchant, Seckill
# Register your models here.
admin.site.register(User)
admin.site.register(Coupon)
admin.site.register(Order)
admin.site.register(Merchant)
admin.site.register(Seckill)

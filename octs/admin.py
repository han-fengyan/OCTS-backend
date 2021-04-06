from django.contrib import admin
import sys
from .models import User, Coupon
# Register your models here.
admin.site.register(User)
admin.site.register(Coupon)
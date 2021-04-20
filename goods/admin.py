from django.contrib import admin
from .models import Good, Picture, Keyword, Category, Favourite

# Register your models here.
admin.site.register(Good)
admin.site.register(Picture)
admin.site.register(Keyword)
admin.site.register(Category)
admin.site.register(Favourite)

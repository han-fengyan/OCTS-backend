from django.contrib import admin
from .models import Good, Picture, Keyword, Tag, Favourite, Draft, Comment, SalePromotion

# Register your models here.
admin.site.register(Good)
admin.site.register(Picture)
admin.site.register(Keyword)
admin.site.register(Tag)
admin.site.register(Favourite)
admin.site.register(Draft)
admin.site.register(Comment)
admin.site.register(SalePromotion)

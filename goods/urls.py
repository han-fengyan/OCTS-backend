from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('upload/', csrf_exempt(views.add_product)),
    path('products/', views.products_list),
    path('list/', views.all_products),
    path('details/<int:id>', views.detail),
    path('modify/', csrf_exempt(views.modify)),
    path('status/', csrf_exempt(views.on_off_shelf)),
    path('search/', views.search),
    path('searchcanary/', views.advanced_search),
    path('favourite/', csrf_exempt(views.collect_favourite)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('upload/', csrf_exempt(views.add)),
    path('list/', views.products_list),
    path('merchant/', views.all_products),
    path('details/<int:id>', views.detail),
    path('modify/<int:id>', csrf_exempt(views.modify)),
    path('offshelf/', csrf_exempt(views.remove)),
]

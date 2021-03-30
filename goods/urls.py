from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.add),
    path('list/', views.products_list),
    path('merchant/', views.all_products),
    path('details/<int:id>', views.detail),
    path('modify/<int:id>', views.modify),
]

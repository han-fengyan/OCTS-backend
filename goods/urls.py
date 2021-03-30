from django.urls import path
from . import views

urlpatterns = [
    path('register_comm/', views.add),
    path('details/<int:id>', views.detail),
]

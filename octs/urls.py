from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('order/', views.order, name='order'),
    path('userorder/',views.userorder,name='userorder'),
    path('orderlist/',views.orderlist,name='orderlist'),
    path('pay/', views.pay,name='pay'),
    path('orderstate/',views.orderstate),
    path('merchantlogin/',views.merchantlogin),
    path('display_money/',views.display_money),
    path('cancel_order/',views.cancel_order),
    path('is_login/',views.is_login),
]
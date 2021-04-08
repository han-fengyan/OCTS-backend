from django.urls import path
# from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [
    path('', views.main_view),
    path('signup/',views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('order/', views.order, name='order'),
    path('userorder/',views.userorder,name='userorder')
]

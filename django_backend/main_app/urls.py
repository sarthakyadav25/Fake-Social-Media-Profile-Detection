from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login', views.login,name="login"),
    path('appadmin',views.admin,name='admin'),
    path('dashboard',views.dashboard,name='dashboard')
]
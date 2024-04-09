from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login1.html', views.login,name="login"),
    path('admin.html',views.admin,name='admin'),
    path('dashboard.html',views.dashboard,name='dashboard')
]
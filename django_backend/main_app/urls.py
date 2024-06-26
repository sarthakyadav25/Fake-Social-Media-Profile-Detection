from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login', views.login,name="login"),
    path('appadmin',views.admin,name='admin'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('predict',views.predict,name='predict'),
    path('detect',views.detect,name='detect'),
    path('logout',views.logout,name='logout'),
    path('notfound',views.notfound,name='notfound'),
    path('verify/<str:token>',views.verify,name='verify'),
    path('reset',views.check_user,name='reset'),
    path('reset_password/<str:token>',views.reset_password,name='resetpassword')
]
from django.http import HttpResponse
from django.shortcuts import render

#path for home page
def index(request):
    return render(request,'index.html')


#path for login page
def login(request):
    return render(request,'login1.html')

#path for admin panel
def admin(request):
    return render(request,'admin.html')

#path for dashboard
def dashboard(request):
    return render(request,'dashboard.html')
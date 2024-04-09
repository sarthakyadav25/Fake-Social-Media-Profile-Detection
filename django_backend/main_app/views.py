from django.http import HttpResponse
from django.shortcuts import render

#path for login page
def Login(request):
    return HttpResponse("Hello this is a detector")
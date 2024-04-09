from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.shortcuts import redirect, render
import pickle
import numpy as np

#path for home page
def index(request):
    return render(request,'index.html')


#path for login page
def login(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        passwd = request.POST['password']
        if name:
            if User.objects.filter(email=email).exists():
                messages.info(request,"Email Exists")
                return redirect('login')
            else:
                user = User.objects.create_user(username=name,email=email,password=passwd)
                user.save()
                return redirect('/')
        else:
            user = auth.authenticate(email=email,password =passwd)
            if user is not None:
                auth.login(request,user)
                return redirect('')
            else:
                messages.info(request,'Invalid Credentials')
                return redirect('login')

    else:
        return render(request,'login1.html')

#path for admin panel
def admin(request):
    return render(request,'admin.html')

#path for dashboard
def dashboard(request):
    return render(request,'dashboard.html')

def predict(request):
    model = pickle.load(open('../django_backend/Machine Learning/model.pkl','rb'))
    features = [1,0.27,0,0,0,53,0,0,32,1000,955]
    final = [np.array(features)]
    prediction = model.predict(final)
    print(prediction)
    if not prediction:
        return HttpResponse("Genuine")
    else:
        return HttpResponse("Fake")

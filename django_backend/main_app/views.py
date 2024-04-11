from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.shortcuts import redirect, render
import pickle
import numpy as np
import instaloader


model = pickle.load(open('../django_backend/Machine Learning/model.pkl','rb'))

#path for home page
def index(request):
    return render(request,'index.html',{"user":request.user})


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

def detect(request):
    return render(request,'detect.html')

def get_instagram_profile_info(username):
    L = instaloader.Instaloader()
    try:
        L.login('tech.nova25', 'syadav@2503')
    except instaloader.exceptions.LoginRequiredException:
        L.interactive_login('tech.nova25')

    profile = instaloader.Profile.from_username(L.context, username)

    return {
        "profile_pic_url": profile.profile_pic_url,
        "num_posts": profile.mediacount,
        "num_followers": profile.followers,
        "num_follows": profile.followees,
        "full_name_words": len(profile.full_name.split()),
        "full_name_length": len(profile.full_name),
        "username_length": len(profile.username),
        "username_equals_fullname": profile.username == profile.full_name,
        "description_length": len(profile.biography),
        "external_url": profile.external_url,
        "private": profile.is_private,
        "username":profile.username,
        "bio":profile.biography,
        "category":profile.business_category_name,
        "fullname":profile.full_name
    }

def predict(request):
    if request.method == "POST":
        profile_link = request.POST['profile_link']
        username = profile_link
    profile_info = get_instagram_profile_info(username)
    profile_pic = profile_info["profile_pic_url"] != None
    username_length = profile_info["username_length"]
    fullname_words = profile_info["full_name_words"]
    nums_length_fullname = profile_info["full_name_length"]
    name_username = profile_info["username_equals_fullname"]
    desc_length = profile_info["description_length"]
    extr_url = profile_info["external_url"] != None
    private = profile_info["private"]
    posts = profile_info["num_posts"]
    followers = profile_info["num_followers"]
    following = profile_info["num_follows"]
    features = [profile_pic,username_length,fullname_words,nums_length_fullname,name_username,desc_length,extr_url,private,posts,followers,following]
    final = [np.array(features)]
    prediction = model.predict(final)
    print(prediction)
    if not prediction:
        profile_info['fake'] = 0
        return render(request,'dashboard.html',{'profile_info':profile_info})
        # return HttpResponse("Genuine")
    else:
        profile_info['fake'] = 1
        # return HttpResponse("Fake")

#logic for logout
def logout(request):
    if request.user:
        auth.logout(request)
        return redirect('/')
    


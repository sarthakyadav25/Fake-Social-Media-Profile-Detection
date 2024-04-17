from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.shortcuts import redirect, render
import pickle
import numpy as np
import instaloader
import requests
import os
import requests
from .models import Profile
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required,user_passes_test



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
                print("email exists...")
                messages.info(request,"Email Exists")
                return redirect('login')
            else:
                print("creating user...")
                user = User.objects.create_user(username=name,email=email)
                user.set_password(passwd)
                user.save()
                return redirect('login')
        else:
            user = auth.authenticate(username=email,password =passwd)
            print(user)
            if user is not None:
                auth.login(request,user)
                return redirect('/')
            else:
                messages.info(request,'Invalid Credentials')
                return redirect('login')

    else:
        return render(request,'login1.html')

#path for admin panel
@user_passes_test(lambda u: u.is_superuser,login_url='/notfound')
def admin(request):
    profiles_searched = Profile.objects.all()
    return render(request,'admin.html',{'user':request.user,'profiles_searched':profiles_searched})

#path for dashboard
@login_required(login_url="login")
def dashboard(request):
    print(request.user)
    return render(request,'dashboard.html')

@login_required(login_url="login")
def detect(request):
    return render(request,'detect.html')

def get_instagram_profile_info(username):
    try:
        L = instaloader.Instaloader()
        try:
            L.login('tech.nova25', r'syadav@2503')
        except instaloader.exceptions.LoginRequiredException:
            L.interactive_login('tech.nova25')
        
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        print(e)
        return HttpResponse(f"<h1>{e}</h1>")

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

@login_required(login_url="login")
def predict(request):
    if request.method == "POST":
        profile_link = request.POST['profile_link']
        username = profile_link
    profile_info = get_instagram_profile_info(username)
    if type(profile_info) != dict:
        return profile_info
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
    if Profile.objects.filter(name=request.user.username,username=profile_info['username']).exists() == False:

        response = requests.get(profile_info['profile_pic_url'])

        # Create a Django Profile object and assign the image to the profile_pic field
        profile = Profile.objects.create(
            name=request.user.username,
            username=profile_info['username'],
            num_posts=posts,
            followers=followers,
            following=following,
            bio=profile_info['bio'],
        )

        # Check if the request was successful
        if response.status_code == 200:
            # Save the image to the profile_pic field
            profile.profile_pic.save(
                f"{profile_info['username']}.jpg",
                ContentFile(response.content),
                save=True
            )
    features = [profile_pic,username_length,fullname_words,nums_length_fullname,name_username,desc_length,extr_url,private,posts,followers,following]
    final = [np.array(features)]
    profile_obj = Profile.objects.get(name=request.user.username,username=profile_info['username'])
    prediction = model.predict(final)
    profile_pic = profile_obj.profile_pic
    if not prediction:
        profile_obj.fake = False
        profile_info['fake'] = 0
    else:
        profile_obj.fake = True
        profile_info['fake'] = 1
    profile_obj.save()
    return render(request,'dashboard.html',{'profile_info':profile_info,'user':request.user,'profile_pic':profile_pic})

#logic for logout
@login_required(login_url="login")
def logout(request):
    if request.user:
        auth.logout(request)
        return redirect('/')
    
#login for a standard not found template
def notfound(request):
    return HttpResponse('<h1>404 Not Found</h1><br><h1>OR</h1><br><h1> Maybe Admin permission required</h1>')


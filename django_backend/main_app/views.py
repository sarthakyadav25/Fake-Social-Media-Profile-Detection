from email import message
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
from .models import Profile,UserProfile
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required,user_passes_test
import uuid
from .utils import send_email,send_reset_email
from .config import envset



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
                user_profile = UserProfile.objects.create(user=user,email_token = str(uuid.uuid4()))
                user_profile.save()
                send_email(email,user_profile.email_token)
                messages.info(request,"Verification email has been sent please verify your account")
                return redirect('login')
        else:
            user = auth.authenticate(username=email,password =passwd)
            if user:
                user_profile = UserProfile.objects.get(user=user)
                if user is not None and user_profile.is_verified:
                    auth.login(request,user)
                    return redirect('/')
                elif user_profile.is_verified == False:
                    messages.info(request,'Please Verify Your Email First Link Has Been Sent')
                    send_email(user.email,user_profile.email_token)
                    return redirect('login')
            else:
                messages.info(request,'Invalid Credentials')
                return redirect('login')

    else:
        return render(request,'login1.html')

#path for admin panel
@user_passes_test(lambda u: u.is_superuser,login_url='/notfound')
def admin(request):
    profiles_searched = Profile.objects.all().order_by('-timestamp')
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
            L.login(envset.instagram_username, envset.instagram_password)
        except instaloader.exceptions.LoginRequiredException:
            L.interactive_login('techinnovate.25')
        
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

#logic for email verification
def verify(request,token):
    try:
        user_profile = UserProfile.objects.get(email_token = token)
        user_profile.is_verified = True
        user_profile.email_token = "0"
        user_profile.save()
        return HttpResponse("Your Email Has Been Verified")
    except Exception as e:
        return HttpResponse("Error In Verifying Email Try Logging In Again")
    
#logic for reset password email input
def check_user(request):
    if request.method == "POST":
        email = request.POST["email"]
        user = User.objects.get(email=email)
        if user:
            user_profile = UserProfile.objects.get(user=user)
            reset_token = str(uuid.uuid4())
            user_profile.reset_password_token = reset_token
            user_profile.save()
            send_reset_email(email,reset_token)
            messages.info(request,"Reset Password Email Has Been Sent To Your Mail Id")
            return redirect('login')
        else:
            messages.info(request,"No User With That Email Exist")
            return redirect('reset')
    else:
        return render(request,'inputmail.html')
    
def reset_password(request,token):
    try:
        user_profile = UserProfile.objects.get(reset_password_token = token)
        if user_profile:
            if request.method == "POST":
                password = request.POST['password']
                cnfpassword = request.POST['cnfpassword']
                if password == cnfpassword:
                    user = user_profile.user
                    user.set_password(password)
                    user.save()
                    user_profile.reset_password_token = "0"
                    user_profile.save()
                    messages.info(request,"Password Reset Successfully")
                    return redirect("login")
                else:
                    messages.info(request,"Passwords Do Not Match")
                    return redirect(f'reset_password/{token}')
            else:
                return render(request,"resetpassword.html")
    except Exception as e:
        return HttpResponse("Link Expired")


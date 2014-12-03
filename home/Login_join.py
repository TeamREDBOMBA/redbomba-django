# -*- coding: utf-8 -*-

# Create your views here.
from redbomba.home.Func import *
import sys
import base64
import requests
import random
from redbomba.home.models import PrivateCard
from redbomba.home.models import UserProfile
from redbomba.home.models import Group
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import strip_tags

######################################## Views ########################################

def register_page(request):
    if request.method=='POST':
        register(request)
    else:
        return HttpResponseRedirect('/home/?msg=200')

def register(request):
    user = User.objects.create_user(
        username=request.POST['username'],
        password=request.POST['password1'],
        email=request.POST['email']
    )
    user.is_active = False
    user.save()
    UserProfile.objects.create(user=user,user_icon="icon/usericon_%d.jpg"%(random.randint(1,10)))
    PrivateCard.objects.create(user=user,contype='sys',con="""%s님. 만나서 반가워요!
이 곳은 %s님에게 관련된 소식만을 모아서 보여주는 활동 스트림 영역입니다.
레드밤바에서 다양한 활동을 즐겨보세요!"""%(user.username,user.username))
    send_complex_message(request.POST['username'])
    user = authenticate(username=request.POST['username'], password=request.POST['password1'])
    if user is not None:
        login(request, user)
        request.session.set_expiry(31536000)
        return HttpResponse("Success")
    else :
        return HttpResponse("Fail")

def verifyEmail(request,id,date_joined):
    id, date_joined = int(id), str(date_joined)
    user = User.objects.get(id=id)
    if date_joined == "" :
        return HttpResponseRedirect('/')
    if user.is_active == False:
        if str(user.date_joined) == base64.urlsafe_b64decode(date_joined):
            user.is_active = True
            user.save()
    if user.is_active == True:
        auth_user = authenticate(username=user.username, password=user.password)
        if auth_user is not None:
            login(request, auth_user)
            request.session.set_expiry(31536000)
            msg = '''
              <html>
              <head>
              <script>
              setInterval("location.href='/';",3000);
              </script>
              </head>
              <body>
              <H1>인증 성공!</H1><br>
              3초 후 자동으로 로그인 됩니다.<br>
              페이지 이동이 안되면 <b><a href='/'>여기</a></b>를 클릭하세요.<br>
              </body>
              </html>
              '''
        else :
            msg = '''
              <html>
              <head>
              <script>
              setInterval("location.href='/';",3000);
              </script>
              </head>
              <body>
              <H1>인증 성공!</H1><br>
              3초 후 메인페이지로 자동 이동합니다.<br>
              페이지 이동이 안되면 <b><a href='/'>여기</a></b>를 클릭하세요.<br>
              </body>
              </html>
              '''
    else:
        msg = "인증 실패!"
    return HttpResponse(msg)

def fncSignupEmail(request):
    email = request.GET.get("email")
    if get_user(email)==None:
        return HttpResponse("")
    else :
        return HttpResponse("이미 등록된 이메일입니다.")

def fncSignupNick(request):
    username = request.GET.get("nick")
    res = get_or_none(User,username=username)
    if res==None:
        return HttpResponse("")
    else :
        return HttpResponse("%s 은(는) 이미 사용 중 입니다." %(username))

def sendVerifyEmail(username):
    user = User.objects.get(username=username)
    email = user.email
    url_link = "http://redbomba.net/auth/%s/%s" %(user.id,base64.urlsafe_b64encode(str(user.date_joined)))
    html_msg = "아래의 인증 링크를 클릭하세요\n<a href='%s'>%s</a>" %(url_link,url_link)
    # html_content = render_to_string('the_template.html', {'varname':'value'}) # ...
    # text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.
    # create the email, and attach the HTML version as well.
    msg = EmailMultiAlternatives('Thanks for signing up with REDBOMBA!', 'REDBOMBA', 'no-reply@redbomba.net', [email])
    msg.attach_alternative(html_msg, "text/html")
    msg.send()

def send_complex_message(username):
    user = User.objects.get(username=username)
    email = user.email
    url_link = "http://redbomba.net/auth/%s/%s" %(user.id,base64.urlsafe_b64encode(str(user.date_joined)))
    html_content = render_to_response('email.html', {'url_link':url_link})
    text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.
    # create the email, and attach the HTML version as well.
    return requests.post(
        "https://api.mailgun.net/v2/redbomba.net/messages",
        auth=("api", "key-2me-oqat4bkqruomgfzrqdhz14hafhr2"),
        files=[],
        data={"from": "Redbomba Team <no-reply@redbomba.net>",
              "to": email,
              "subject": "Thanks for signing up with REDBOMBA!",
              "text": text_content,
              "html": html_content})
# -*- coding: utf-8 -*-

import base64
import random

import requests
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt

from redbomba.home.models import UserProfile, get_or_none


# Create your views here.

def home(request, msg=None):
    if request.user.is_anonymous() == False :
        return HttpResponseRedirect('/')
    context = {'msg':msg}
    return render(request, 'home.html', context)


def home_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def home_login(request):
    try:
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = get_or_none(User,email=email.lower())
        next = request.POST.get("next","/")
        if username :
            user = authenticate(username=username, password=password)
            login(request, user)
            request.session.set_expiry(31536000)
            return HttpResponseRedirect(next)
        return home(request, msg=u"존재하지 않는 계정입니다.")
    except Exception as e :
        return home(request, msg=u"존재하지 않는 계정입니다.")

def home_join(request):
    username = request.POST.get("username")
    passwd = request.POST.get("password1")
    email = request.POST.get("email")
    user = User.objects.create_user(username=username,password=passwd,email=email)
    user.is_active = False
    user.save()
    UserProfile.objects.create(user=user)
    #     PrivateCard.objects.create(user=user,contype='sys',con="""%s님. 만나서 반가워요!
    # 이 곳은 %s님에게 관련된 소식만을 모아서 보여주는 활동 스트림 영역입니다.
    # 레드밤바에서 다양한 활동을 즐겨보세요!"""%(user.username,user.username))
    send_complex_message(username)
    user = authenticate(username=username, password=passwd)
    if user:
        login(request, user)
        request.session.set_expiry(31536000)
        return HttpResponseRedirect('/')
    else :
        return home(request, msg=u"생성할 수 없는 계정입니다.")

@csrf_exempt
def home_join_chkEmail(request):
    email = request.GET.get("email")
    if get_or_none(User,email=email.lower()):
        return HttpResponse(u"이미 등록된 이메일입니다.")
    else :
        return HttpResponse("")

@csrf_exempt
def home_join_chkNick(request):
    username = request.GET.get("nick")
    res = get_or_none(User,username=username)
    if res :
        return HttpResponse(u"%s 은(는) 이미 사용 중 입니다." %(username))
    else :
        return HttpResponse("")

def home_verify(request,id,date_joined):
    id, date_joined = int(id), str(date_joined)
    user = get_or_none(User,id=id)
    if date_joined == "" :
        return HttpResponseRedirect('/')
    if user.is_active == False:
        if str(user.date_joined) == base64.urlsafe_b64decode(date_joined):
            user.is_active = True
            user.save()
    if user.is_active == True:
        auth_user = authenticate(username=user.username, password=user.password)
        if auth_user :
            login(request, auth_user)
            request.session.set_expiry(31536000)
        msg = u'''
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
    else:
        msg = "인증 실패!"
    return HttpResponse(msg)

def send_complex_message(username):
    user = get_or_none(User,username=username)
    email = user.email
    url_link = "http://redbomba.net/home/verify/%s/%s" %(user.id,base64.urlsafe_b64encode(str(user.date_joined)))
    html_content = render_to_response('home_email.html', {'url_link':url_link})
    text_content = strip_tags(html_content)
    return requests.post(
        "https://api.mailgun.net/v2/redbomba.net/messages",
        auth=("api", "key-84c68ec43394478a9ae518451102b3e4"),
        files=[],
        data={"from": "Redbomba Team <no-reply@redbomba.net>",
              "to": email,
              "subject": "Thanks for signing up with REDBOMBA!",
              "html": html_content})
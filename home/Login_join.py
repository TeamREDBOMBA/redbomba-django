# -*- coding: utf-8 -*-
 
# Create your views here.
from redbomba.home.Func import *
import base64
import requests
import random
from redbomba.home.forms import *
from redbomba.home.models import UserProfile
from redbomba.home.models import Group
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags

######################################## Views ########################################

def register_page(request):
  if request.method=='POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      user = User.objects.create_user(
        username=form.cleaned_data['username'],
        password=form.cleaned_data['password1'],
        email=form.cleaned_data['email'],
      )
    user = User.objects.get(username=form.cleaned_data['username'])
    user.is_active = False
    user.save()
    UserProfile.objects.create(user_id=user.id,user_icon=random.randint(1,10))
    send_complex_message(form.cleaned_data['username'])
    return HttpResponseRedirect('/home/?msg=201&site=%s'%(form.cleaned_data['email'].split('@', 1)[-1]))
  else:
    return HttpResponseRedirect('/home/?msg=200')
    
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
    msg = '''
      <html>
      <head>
      <script>
      setInterval("location.href='http://redbomba.net/';",3000);
      </script>
      </head>
      <body>
      <H1>인증 성공!</H1><br>
      3초 후 메인페이지로 자동 이동합니다.<br>
      페이지 이동이 안되면 <b><a href='http://redbomba.net'>여기</a></b>를 클릭하세요.<br>
      </body>
      </html>
      '''
  else:
    msg = "인증 실패!"
  
  return HttpResponse(msg)
  
def fncSignupEmail(request):
  email = request.GET["email"]
  if get_user(email)==None:
    return HttpResponse("")
  else :
    return HttpResponse("이미 등록된 이메일입니다.")

def fncSignupNick(request):
  username = request.GET["nick"]
  try:
      res = User.objects.get(username=username)
  except User.DoesNotExist:
      res =  None
  if res==None:
    return HttpResponse("")
  else :
    return HttpResponse("%s 은(는) 이미 사용 중 입니다." %(username))
    
def fncGroupName(request):
  groupname = request.GET["name"]
  try:
      res = Group.objects.get(name=groupname)
  except Exception as e:
      res =  None
  if res==None:
    return HttpResponse("")
  else :
    return HttpResponse("%s 은(는) 이미 사용 중 입니다." %(groupname))
    
def fncGroupNick(request):
  groupnick = request.GET["nick"]
  try:
      res = Group.objects.get(nick=groupnick)
  except Exception as e:
      res =  None
  if res==None:
    return HttpResponse("")
  else :
    return HttpResponse("%s 은(는) 이미 사용 중 입니다." %(groupnick))
  
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
  # html_content = render_to_string('email.html', {'url_link':url_link})
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
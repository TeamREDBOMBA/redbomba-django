# -*- coding: utf-8 -*-
 
# Create your views here.
from redbomba.home.Func import *
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect

######################################## Views ########################################

def logout_page(request):
    logout(request)
     
    return HttpResponseRedirect('/')

def email_login_view(request):
  try:
    email = request.POST["email"]
    password = request.POST["password"]
    username = get_user(email)
    if username is None:
      return HttpResponseRedirect('/home/?msg=101')
    else :
      user = authenticate(username=username, password=password)
      if user is not None:
          if user.is_active:
              login(request, user)
              request.session.set_expiry(31536000)
              return HttpResponseRedirect('/')
          else:
              return HttpResponseRedirect('/home/?msg=110')
      else:
          return HttpResponseRedirect('/home/?msg=102')
  except ValueError:
    return HttpResponseRedirect('/home/?msg=100')
  except ZeroDivisionError:
    return HttpResponseRedirect('/home/?msg=100')
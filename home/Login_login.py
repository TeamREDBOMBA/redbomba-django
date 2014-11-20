# -*- coding: utf-8 -*-
 
# Create your views here.
from redbomba.home.Func import *
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect

######################################## Views ########################################

def logout_page(request):
    logout(request)
     
    return HttpResponseRedirect('/')

def email_login_view(request):
  try:
    email = request.POST["email"]
    password = request.POST["password"]
    username = get_user(email)
    next = request.POST["next"]
    if username is None:
      return HttpResponseRedirect('/home/?msg=101')
    else :
      user = authenticate(username=username, password=password)
      login(request, user)
      request.session.set_expiry(31536000)
      return HttpResponseRedirect(next)
  except ValueError:
    return HttpResponseRedirect('/home/?msg=100')
  except ZeroDivisionError:
    return HttpResponseRedirect('/home/?msg=100')
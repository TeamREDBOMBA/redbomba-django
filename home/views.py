# -*- coding: utf-8 -*-
 
# Create your views here.
from redbomba.home.Func import *
from redbomba.home.Arena_card import *
from redbomba.home.Arena_matchmaker import *
from redbomba.home.Battle import *
from redbomba.home.Feed import *
from redbomba.home.Head_group import *
from redbomba.home.Head_notification import *
from redbomba.home.Head_search import *
from redbomba.home.Login_join import *
from redbomba.home.Login_login import *
from redbomba.home.Main import *
from redbomba.home.Mobile import *
from redbomba.home.Stats_gamelink import *
from redbomba.home.Stats_myarena import *

def home(request):
    context = ''
    if request.GET.get('msg'):
        context= errorMsg(request.GET.get('msg'))
        context['site'] = request.GET.get('site')
    return render(request, 'login.html', context)

def main(request):
    try:
      gl = GameLink.objects.filter(uid=request.user)
      gl_h = 100.0/int(gl.count())
      try:
        group = GroupMember.objects.get(Q(uid=request.user)&~Q(is_active=-1)).gid
        groupmem = GroupMember.objects.filter(Q(gid=group)&~Q(is_active=-1))
      except Exception as e:
        group = None
        groupmem = None
      get_group = request.GET.get('group')
      context = {
        'user': request.user,
        'uinfo':request.user.get_profile,
        'group':group,
        'groupmem':groupmem,
        'get_group':get_group,
        'gamelink':gl,
        'height':gl_h,
        'from':'/'
        }
    except Exception as e:
      context = {'user': request.user}
    return render(request, 'main.html', context)

def stats(request,username=None):
    try:
      myuid = request.user
      if username :
        target_uid = User.objects.get(username=username)
      else :
        target_uid = myuid

      try:
        getval = request.GET['get']
      except Exception as e:
        getval = ""

      try:
        gl = GameLink.objects.filter(uid=target_uid)
      except Exception as e:
        gl=None

      try:
        group = GroupMember.objects.get(Q(uid=target_uid)&~Q(is_active=-1)).gid
        groupmem = GroupMember.objects.filter(Q(gid=group)&~Q(is_active=-1))
      except Exception as e:
        group = None
        groupmem = None

      try:
        if request.GET['group']:
          get_group = request.GET['group']
        else :
          get_group = None
      except Exception as e:
        get_group = None

      context = {
        'user' : request.user,
        'uinfo':request.user.get_profile,
        'target_user':target_uid,
        'group':group,
        'groupmem':groupmem,
        'get_group':get_group,
        'gamelink' : gl,
        'getval':getval,
        'from' : '/stats/'
        }
    except Exception as e:
      context = {'user': request.user}
    return render(request, 'stats.html', context)

def arena(request):
    try:
      try:
        getval = request.GET['get']
      except Exception as e:
        getval = ""

      try:
        group = GroupMember.objects.get(Q(uid=request.user)&~Q(is_active=-1)).gid
        groupmem = GroupMember.objects.filter(Q(gid=group)&~Q(is_active=-1))
      except Exception as e:
        group = None
        groupmem = None

      try:
        if request.GET['group']:
          get_group = request.GET['group']
        else :
          get_group = None
      except Exception as e:
        get_group = None

      try:
        is_pass1 = int(Tutorial.objects.get(uid=request.user).is_pass1)
      except Exception as e:
        is_pass1 = 0

      state = {"is_pass1":is_pass1}

      context = {
        'user': request.user,
        'uinfo' : request.user.get_profile,
        'group':group,
        'groupmem':groupmem,
        'get_group':get_group,
        'getval':getval,
        'state':state,
        'from' : '/arena/'
        }
    except Exception as e:
      context = {'user': request.user}
    return render(request, 'arena.html', context)

def test(request):
  #send_complex_message(request.user.username)
  return HttpResponse('ok?')
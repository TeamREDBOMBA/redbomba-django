# -*- coding: utf-8 -*-
 
# Create your views here.
from redbomba.home.Func import *
from redbomba.home.models import *
from bs4 import BeautifulSoup
from django import template
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.template.loader import get_template, render_to_string
from django.utils import simplejson

######################################## Views ########################################

def getField(request) :
  if request.user is not None :
    try :
      query_g = GroupMember.objects.filter(uid=request.user)
      groups = []
      for val in query_g:
        try :
          gm_count = GroupMember.objects.filter(gid=val.gid,is_active=1).count()
        except Exception as e:
          gm_count = 0
        groups.append({'gid':val.gid,'count':gm_count})

      user = GroupMember.objects.get(uid=request.user)
      query_l = League.objects.filter(id__in=LeagueTeam.objects.filter(group_id=user.gid).values_list('round__league_id', flat=True))
      leagues = []
      for val in query_l:
        ls = remakeLeagueState(val,user)
        leagues.append(ls)
      context = {"groups":groups,"leagues":leagues}
      return render(request, 'field.html', context)
    except Exception as e:
      context = {"groups":None,"leagues":None}
      return render(request, 'field.html', context)
  return HttpResponse("error")
    
def getGroup(request):
  if request.method=='POST':
    try :
      if request.user.username != request.POST['username'] :
        uid = User.objects.get(username=request.POST['username']).id
      else :
        uid = request.user.id
      return HttpResponse(groupsorter(uid, request))
    except Exception as e:
      return HttpResponse("Input error:"+e.message)
  else :
    return HttpResponse("Input error")

def getGroupMember(request):
  if request.method=='POST':
    try :
      if request.user.username != request.POST['username'] :
        uid = User.objects.get(username=request.POST['username']).id
      else :
        uid = request.user.id
      gid = request.POST["gid"]
      return HttpResponse(groupmembersorter(uid,gid))
    except Exception as e:
      return HttpResponse("Input error:"+e.message)
  else :
    return HttpResponse("Input error")
    
def getGroupList(request):
  if request.method=='POST':
    uid = request.user
    action = request.POST["action"]
    try:
      text = request.POST["text"]
    except Exception as e:
      text = ""
    if action == "insert" :
      query_g = GroupMember.objects.all().values_list('uid', flat=True)
      query_u = User.objects.filter(~Q(id__in=query_g),Q(username__icontains=text))
      query = []
      for val in query_u:
        query.append({'id':val.id, 'username':val.username, 'user_icon':val.get_profile().user_icon})
      context = { 'user': query, 'gid':GroupMember.objects.get(uid=uid).gid.id, 'mode':action }
      return render(request, 'groupmemlist.html', context)
    else :
      query_g = GroupMember.objects.filter(~Q(uid=uid),Q(gid=Group.objects.get(id=request.POST["gid"]))).values_list('uid', flat=True)
      query_u = User.objects.filter(Q(id__in=query_g),Q(username__icontains=text))
      query = []
      for val in query_u:
        query.append({'id':val.id, 'username':val.username, 'user_icon':val.get_profile().user_icon})
      context = { 'user': query, 'gid':GroupMember.objects.get(uid=uid).gid.id, 'mode':action }
      return render(request, 'groupmemlist.html', context)
  else:
    return HttpResponse("Request Error")

def getGroupInfo(request):
  if request.method=='POST':
    gid = request.POST['group']
    try:
      group = Group.objects.get(id=gid)
      groupmem = GroupMember.objects.filter(Q(gid=group)&Q(is_active=1)).order_by("order")
      inviting = GroupMember.objects.filter(Q(gid=group)&Q(is_active=0))
      waitting = GroupMember.objects.filter(Q(gid=group)&Q(is_active=-1))
    except Exception as e:
      group = None
      groupmem = None
      inviting = None
      waitting = None
    try:
      isAdmin = Group.objects.filter(id=gid,uid=request.user).count()
      isMem = GroupMember.objects.filter(Q(gid=group)&Q(uid=request.user)&Q(is_active=1)).count()
      isWait = GroupMember.objects.filter(Q(gid=group)&Q(uid=request.user)&Q(is_active=-1)).count()
      isInv = GroupMember.objects.filter(Q(gid=group)&Q(uid=request.user)&Q(is_active=0)).count()
      info = {"isAdmin":isAdmin, "isMem":isMem, "isWait":isWait, "isInv":isInv}
    except Exception as e:
      info = {"isAdmin":0, "isMem":0, "isWait":0, "isInv":0}
    context = {
      'user': request.user,
      'group':group,
      'groupmem':groupmem,
      'inviting':inviting,
      'waitting':waitting,
      'info':info,
      }
    return render(request, 'group_info.html', context)
  else:
    return HttpResponse("Request Error")

def getGroupInfoOrder(request):
  if request.method=='POST':
    if request.POST['action'] == "get" :
      gid = request.POST['group']
      try:
        group = Group.objects.get(id=gid)
        groupmem = GroupMember.objects.filter(Q(gid=group)&Q(is_active=1)).order_by("order")
      except Exception as e:
        groupmem = None

      context = {
        'groupmem':groupmem
      }
      return render(request, 'group_info_order.html', context)
    else :
      arr_list =  simplejson.loads(request.POST['memlist'])
      num = 0
      for al in arr_list:
        al = al.replace("div_","")
        gm = GroupMember.objects.get(uid=al)
        gm.order = num
        gm.save()
        num = num + 1
      return HttpResponse("Success")
  else:
    return HttpResponse("Request Error")

def write_Group(request):
  if request.method=='POST':
    action = request.POST["action"]
    if action == "insert" :
      group = Group.objects.create(
        name=request.POST["name"],
        nick=request.POST["nick"],
        uid=request.user,
        group_icon='common.png',
        game=Game.objects.get(name=request.POST["game"])
        )
      try:
        GroupMember.objects.get(
          gid=group,
          uid=request.user,
          is_active=1
          )
      except Exception as e:
        GroupMember.objects.create(
          gid=group,
          uid=request.user,
          is_active=1
          )
      return HttpResponse("Success")
    else :
      gid = request.POST["gid"]
      group = Group.objects.get(id=gid)
      GroupMember.objects.filter(gid=group).delete()
      group.delete()
      return HttpResponse("Success")
  else:
    return HttpResponse("error")
    
def setGroupMember(request):
  if request.method=='POST':
    action = request.POST["action"]
    user = request.user
    try:
      user = User.objects.get(username=request.POST["username"])
    except Exception as e:
      user = request.user
    if action == "yes" :
      group = Group.objects.get(id=request.POST["gid"])
      gm = GroupMember.objects.get(Q(gid=group)&Q(uid=user)&~Q(is_active=1))
      gm.is_active = 1
      gm.save()
    else:
      group = Group.objects.get(id=request.POST["gid"])
      GroupMember.objects.filter(Q(gid=group)&Q(uid=user)&~Q(is_active=1)).delete()
    return HttpResponse("Success")
  else:
    return HttpResponse("error")

def setGroupList(request):
  if request.method=='POST':
    try:
      action = request.POST["action"]
      group = Group.objects.get(id=request.POST["gid"])
      if action == "Join" :
        try:
          gm=GroupMember.objects.get(gid=group,uid=request.user)
        except Exception as e:
          GroupMember.objects.create(gid=group,uid=request.user,is_active=-1)
      elif action == "Quit" :
        GroupMember.objects.filter(gid=group,uid=request.user).delete()
      elif group == Group.objects.get(uid=request.user) :
        user = User.objects.get(username=request.POST["username"])
        if action == "insert" :
          try:
            gm=GroupMember.objects.get(gid=group,uid=user)
          except Exception as e:
            GroupMember.objects.create(gid=group,uid=user,is_active=0)
        elif action == "changeLeader" :
          if GroupMember.objects.filter(gid=group,uid=user).count() :
            group.uid = user
            group.save()
        else:
          GroupMember.objects.filter(gid=group,uid=user).delete()
      else:
        return HttpResponse("error")
      return HttpResponse("Success")
    except Exception as e:
      return HttpResponse("error")
  else:
    return HttpResponse("error")

def getChatting(request):
  if request.user :
    len = int(request.POST["len"])
    group = Group.objects.get(name=request.POST["group_name"])
    chatting = Chatting.objects.filter(gid=group).order_by("-date_updated")
    val = ""
    i=0
    for chatElem in chatting:
      if i==len: break
      username = chatElem.uid.username
      con = chatElem.con
      if username == request.user.username:
        output = "<span class='username myname'>%s</span> : %s<br/>"%(username,con)
      elif username == "redbomba":
        output = "<span class='username myname'><font color='#e74c3c'>RED</font>BOMBA</span> : %s<br/>"%(con)
      else :
        output = "<span class='username'>%s</span> : %s<br/>"%(username,con)
      val = output+val
      i=i+1
    return HttpResponse(val)
  return HttpResponse('ERROR')

def groupsorter(uid, request):
  val = ""
  query_gm = GroupMember.objects.filter(Q(uid=User.objects.get(id=uid))&~Q(is_active=-1))
  if query_gm :
    template = get_template('group.html')
    for gmElem in query_gm:
      query_group = Group.objects.get(id=gmElem.gid.id)
      if query_group.uid.id == gmElem.uid.id:
        host = "host"
      else :
        host = ""
      variables = Context({
      'group' : query_group,
      'is_active' : gmElem.is_active,
      'host':host,
      'target_user':uid,
      'user':request.user
      })
      output = template.render(variables)
      val = val+output;
  else :
    template = get_template('groupadd.html')
    variables = Context({
      'target_user':uid,
      'user':request.user
    })
    output = template.render(variables)
    val = output;
  return val

def groupmembersorter(uid,gid):
  val = ""
  if GroupMember.objects.get(Q(gid=Group.objects.get(id=gid))&Q(uid=User.objects.get(id=uid))&~Q(is_active=-1)) :
    query_gm = GroupMember.objects.filter(Q(gid=Group.objects.get(id=gid))&~Q(is_active=-1)).order_by('uid')
    template = get_template('groupmember.html')
    for gmElem in query_gm:
      if Group.objects.get(id=gmElem.gid.id).uid.id == gmElem.uid.id:
        host = "host"
      else :
        host = ""
      user = User.objects.get(id=gmElem.uid.id)
      variables = Context({
      'group_user' : user,
      'group_active':gmElem.is_active,
      'is_active' : GroupMember.objects.get(gid=Group.objects.get(id=gid),uid=User.objects.get(id=uid)).is_active,
      'host' : host,
      'uinfo':user.get_profile
      })
      output = template.render(variables)
      val = val+output;
  else :
    val = None
  return val


def remakeLeagueState(l, u):
  ls = LeagueState(l,u)
  if ls['no'] == 1 :
    try :
      noti = Notification.objects.get(tablename='home_league',contents=ls['league'].id,uid=ls['user'].uid)
    except Exception as e:
      noti = None
    state = {"no":ls['no'],"league":ls['league'],"user":ls['user'],"round":ls['lt'].round,"noti":noti}
  elif ls['no'] == 2 :
    try :
      noti = Notification.objects.get(tablename='home_leagueround',contents=ls['lm'].team_a.round.id,uid=ls['user'].uid)
    except Exception as e:
      noti = None
    state = {"no":ls['no'],"league":ls['league'],"user":ls['user'],"lm":ls['lm'],"noti":noti}
  elif ls['no'] == 3 :
    try :
      noti = Notification.objects.get(tablename='home_leaguematch',contents=ls['lm'].id,uid=ls['user'].uid)
    except Exception as e:
      noti = None
    state = {"no":ls['no'],"league":ls['league'],"user":ls['user'],"msg":"배틀페이지 입장이 가능합니다.","lr":ls['lm'].team_a.round.id,"noti":noti}
  else :
    state = None
  return state
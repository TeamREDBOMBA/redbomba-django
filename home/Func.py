# -*- coding: utf-8 -*-
 
# Create your views here.
import base64
import re, urlparse
import requests
import json
import urllib2
from redbomba.home.models import Smile
from redbomba.home.models import Group
from redbomba.home.models import GroupMember
from redbomba.home.models import Game
from redbomba.home.models import GameLink
from redbomba.home.models import Notification
from redbomba.home.models import League
from redbomba.home.models import LeagueTeam
from redbomba.home.models import LeagueRound
from redbomba.home.models import LeagueMatch
from django import template
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags
from datetime import date, datetime, timedelta
from django.utils.timezone import utc
from django.utils import timezone

def get_user(email):
    try:
        return User.objects.get(email=email.lower())
    except User.DoesNotExist:
        return None

def forsocket(request):
  val = ""
  if request.method=='POST':
    try:
      uid = request.user
      gid = GroupMember.objects.get(uid=uid).gid
      val = val + "<uid>%s</uid>" %(uid.id)
      val = val + "<gid>%s</gid>" %(gid.id)
    except Exception as e:
      val = val + "<uid>%s</uid>" %(uid.id)
      val = val + "<gid>0</gid>"
  else:
    val = "POST ERROR"
  return HttpResponse(val)

def errorMsg(msg) :
  if msg=='100':
    return {'msg':msg,'con':'로그인 중 오류가 발생하였습니다. 다시 시도해 주십시오.'}
  elif msg=='101':
    return {'msg':msg,'con':'E-mail이 틀렸습니다.'}
  elif msg=='102':
    return {'msg':msg,'con':'Password가 틀렸습니다.'}
  elif msg=='110':
    return {'msg':msg,'con':'이메일 인증이 필요합니다.'}
  elif msg=='200':
    return {'msg':msg,'con':'회원가입 중 오류가 발생하였습니다. 다시 시도해 주십시오.'}
  elif msg=='201':
    return {'msg':msg,'title':'축하합니다.','con':'게이머의 세상, REDBOMBA에 오신 것을 환영합니다.'}
  elif msg=='300':
    return {'msg':msg,'con':'그룹생성 중 오류가 발생하였습니다. 다시 시도해 주십시오.'}
  elif msg=='301':
    return {'msg':msg,'con':'그룹이 생성되었습니다. 그룹원을 모집해보세요.'}
  
def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

def LeagueState(league, user):
  state = {}
  lr = LeagueRound.objects.filter(league_id=league).order_by("round")

  try:
    Group.objects.get(uid=user.uid)
    isAdmin = 1
  except Exception as e:
    isAdmin = 0

  try:
    if LeagueTeam.objects.filter(group_id=user.gid,round__in=lr).order_by("-round")[0].round.round != 1 :
      last_lt = LeagueTeam.objects.filter(group_id=user.gid,round__in=lr).order_by("-round")[1]
      last_lm = LeagueMatch.objects.filter(Q(team_a=last_lt)|Q(team_b=last_lt)).order_by("-game")[0]
    else :
      last_lt = LeagueTeam.objects.filter(group_id=user.gid,round__in=lr).order_by("-round")[0]
      last_lm = LeagueMatch.objects.filter(Q(team_a=last_lt)|Q(team_b=last_lt)).order_by("-game")[0]
  except Exception as e:
    last_lm = None

  try:
    last_round = lr.order_by("-round")
    if LeagueMatch.objects.filter(team_a__round=last_round[0]).order_by("-game")[0].state == 10 :
      final = LeagueMatch.objects.filter(team_a__round=last_round[0]).order_by("-game")[0]
      semifinal = LeagueMatch.objects.filter(team_a__in=LeagueTeam.objects.filter(round=last_round[1])).order_by("-game")[0]
      if final.result == 'A':
        win_1 = final.team_a.group_id
        win_2 = final.team_b.group_id
      else:
        win_2 = final.team_a.group_id
        win_1 = final.team_b.group_id
      if semifinal[0].result == 'A':
        win_3_1 = semifinal[0].team_b.group_id
      else :
        win_3_1 = semifinal[0].team_a.group_id
      if semifinal[1].result == 'A':
        win_3_2 = semifinal[1].team_b.group_id
      else :
        win_3_2 = semifinal[1].team_a.group_id
      state = {"no":5,"win_1":win_1,"win_2":win_2,"win_3_1":win_3_1,"win_3_2":win_3_2,"last_lm":last_lm,"isAdmin":isAdmin,"user":user,"league":league}
      return state
  except Exception as e:
    pass

  try:
    all1_lt = LeagueTeam.objects.filter(round=lr[1],round__league_id=league)
    now = datetime.utcnow().replace(tzinfo=utc)
    if all1_lt.count():
      all2_lt = LeagueTeam.objects.filter(id__in=all1_lt,group_id=user.gid)
      if all2_lt.count() == 0:
        state = {"no":4,"last_lm":last_lm,"lr":all1_lt[0].round,"lt":all1_lt.filter(group_id=user.gid)[0],"isAdmin":isAdmin,"user":user,"league":league,"zz":1}
        return state
    elif LeagueTeam.objects.filter(round=lr[0],round__league_id=league).count() == 0 and lr[0].league_id.end_apply < now :
      state = {"no":4,"last_lm":last_lm,"lr":lr[0],"isAdmin":isAdmin,"user":user,"league":league,"zz":2}
      return state
  except Exception as e:
    state = {"no":4,"last_lm":last_lm,"lr":all1_lt[0].round,"isAdmin":isAdmin,"user":user,"league":league,"zz":3,"e":e.message}
    return state

  try:
    lt = LeagueTeam.objects.filter(group_id=user.gid,round__in=lr).order_by("-round")[0]
  except Exception as e:
    try:
      groupmem = GroupMember.objects.filter(gid=user.gid,is_active=1).count()
    except Exception as e:
      groupmem = 0
    try:
      gamelink = GameLink.objects.filter(uid__in=GroupMember.objects.filter(gid=user.gid,is_active=1).values_list('uid', flat=True)).count()
    except Exception as e:
      gamelink = 0
    if isAdmin == 0 or groupmem < 5 or gamelink < 5 :
      state = {"no":-1,"e":e.message,"isAdmin":isAdmin,"user":user,"league":league,"lr":lr[0],"groupmem":groupmem, "gamelink":gamelink}
      return state
    state = {"no":0,"e":e.message,"isAdmin":isAdmin,"user":user,"league":league,"lr":lr[0]}
    return state

  try:
    lm = LeagueMatch.objects.filter(Q(team_a=lt)|Q(team_b=lt)).order_by("-game")[0]
  except Exception as e:
    state = {"no":1,"lt":lt,"last_lm":last_lm,"e":e.message,"isAdmin":isAdmin,"user":user,"league":league}
    return state

  try:
    now = datetime.utcnow().replace(tzinfo=utc) + timedelta(minutes=30)
    lm = LeagueMatch.objects.filter(id=lm.id,date_match__lte=now).order_by("-game")[0]
  except Exception as e:
    state = {"no":2,"lm":lm,"last_lm":last_lm,"e":e.message,"isAdmin":isAdmin,"user":user,"league":league}
    return state

  try:
    lm = LeagueMatch.objects.filter(Q(id=lm.id)&Q(state="10")).order_by("-game")[0]
    if lm.result == 'A' and lm.team_a.group_id == user.gid :
      next_lt = LeagueTeam.objects.get(Q(group_id=user.gid)&Q(round_round=lm.team_a.round.round+1))
    elif lm.result == 'B' and lm.team_b.group_id == user.gid :
      next_lt = LeagueTeam.objects.get(Q(group_id=user.gid)&Q(round_round=lm.team_a.round.round+1))
    else :
      return {"no":4,"last_lm":last_lm,"lr":lr[0],"isAdmin":isAdmin,"user":user,"league":league}
  except Exception as e:
    state = {"no":3,"lm":lm,"last_lm":last_lm,"isAdmin":isAdmin,"user":user,"league":league}
    return state

  last_lt = LeagueTeam.objects.filter(group_id=user.gid,round__in=lr).order_by("-round")[0]
  last_lm = LeagueMatch.objects.filter(Q(team_a=last_lt)|Q(team_b=last_lt)).order_by("-game")[0]

  last_round = lr.order_by("-round")
  final = lm
  semifinal = LeagueMatch.objects.filter(team_a__in=LeagueTeam.objects.filter(round=last_round[1])).order_by("-game")[0]
  if final.result == 'A':
    win_1 = final.team_a.group_id
    win_2 = final.team_b.group_id
  else:
    win_2 = final.team_a.group_id
    win_1 = final.team_b.group_id
  if semifinal[0].result == 'A':
    win_3_1 = semifinal[0].team_b.group_id
  else :
    win_3_1 = semifinal[0].team_a.group_id
  if semifinal[1].result == 'A':
    win_3_2 = semifinal[1].team_b.group_id
  else :
    win_3_2 = semifinal[1].team_a.group_id

  state = {"no":5,"win_1":win_1,"win_2":win_2,"win_3_1":win_3_1,"win_3_2":win_3_2,"last_lm":last_lm,"isAdmin":isAdmin,"user":user,"league":league,"last_round":last_round}
  return state

def get_json(url) :
  j = urllib2.urlopen(url)
  j_obj = json.load(j)
  return j_obj
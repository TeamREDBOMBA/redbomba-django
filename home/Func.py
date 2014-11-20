# -*- coding: utf-8 -*-

# Create your views here.
from math import log
import sys
import os
import pwd
import re, urlparse
import json
import urllib2
import requests
from redbomba.home.models import Group, Notification
from redbomba.home.models import GroupMember
from redbomba.home.models import GameLink
from redbomba.home.models import LeagueTeam
from redbomba.home.models import LeagueRound
from redbomba.home.models import LeagueMatch
from datetime import timedelta, datetime
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateformat import format

# print >>sys.stderr, "%s"%(gm) # Log

def get_user(email):
    try:
        return User.objects.get(email=email.lower())
    except User.DoesNotExist:
        return None

def forsocket(request):
    val = ""
    if request.method=='POST':
        uid = request.user
        gid =get_or_none(GroupMember,user=uid)
        if gid == None : gid = 0
        val = val + "<uid>%s</uid>" %(uid.id)
        val = val + "<gid>%s</gid>" %(gid.id)
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

def get_json(url) :
    j = urllib2.urlopen(url)
    j_obj = json.load(j)
    return j_obj

def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def upload(request):
    errorMsg = ""
    UPLOAD_DIR = "/media/upload/files_%s" %(format(timezone.localtime(timezone.now()), u'U'))
    errorMsg = errorMsg +"<br/>"+"dir:"+ UPLOAD_DIR
    if request.method == 'POST':
        if 'file' in request.FILES:
            if not os.path.exists("redbomba"+UPLOAD_DIR):
                os.makedirs("redbomba"+UPLOAD_DIR)
                uid, gid =  pwd.getpwnam('root').pw_uid, pwd.getpwnam('root').pw_uid
                os.chown("redbomba"+UPLOAD_DIR, uid, gid)
            file = request.FILES['file']
            filename = file._name
            errorMsg = errorMsg +"<br/>"+"filename:"+ filename
            fp = open('%s/%s' % ("redbomba"+UPLOAD_DIR, filename) , 'wb')
            for chunk in file.chunks():
                fp.write(chunk)
            fp.close()
            return "%s/%s"%(UPLOAD_DIR, filename)
    return 'Failed ' + errorMsg

def remakeLeagueState(l, u):
    ls = LeagueState(l,u)
    if ls['no'] == 1 :
        noti = get_or_none(Notification,action='League_JoinLeague',contents=ls['league'].id,user=ls['user'])
        state = {"no":ls['no'],"league":ls['league'],"user":get_or_none(GroupMember,user=ls['user']),"round":ls['lt'].round,"noti":noti}
    elif ls['no'] == 2 :
        noti = get_or_none(Notification,action='League_RunMatchMaker',contents=ls['lm'].team_a.round.id,user=ls['user'])
        state = {"no":ls['no'],"league":ls['league'],"user":get_or_none(GroupMember,user=ls['user']),"lm":ls['lm'],"noti":noti}
    elif ls['no'] == 3 :
        noti = get_or_none(Notification,action='League_StartMatch',contents=ls['lm'].id,user=ls['user'])
        state = {"no":ls['no'],"league":ls['league'],"user":get_or_none(GroupMember,usdr=ls['user']),"msg":"배틀페이지 입장이 가능합니다.","lr":ls['lm'].team_a.round.id,"noti":noti}
    else :
        state = None
    return state

def LeagueState(league, user):

    no = "ERROR"

    #User State
    isFiveMem = IsFiveMem(user)                     # 1
    isFiveLink = IsFiveLink(league, user)           # 2
    isLeader = IsLeader(user)                       # 3
    isInGroup = IsInGroup(user)                     # 4
    isHost = IsHost(league,user)                    # HOST

    #League State
    isStartApply = IsStartApply(league)             # 5
    isFullLeague = IsFullLeague(league)             # 6
    isEndApply = IsEndApply(league)                 # 8
    isFinishLeague = IsFinishLeague(league)         # 12
    isStart1stMatch = IsStart1stMatch(league)       # 9-2
    nowRound = NowRound(league)
    canMatchMaker = CanMatchMaker(nowRound)

    #User&League State
    isCompleteJoin = IsCompleteJoin(league, user)   # 7
    isRunMathMaker = IsRunMathMaker(isCompleteJoin) # 9-1
    isCanBattle = IsCanBattle(isRunMathMaker)       # 10
    isFinishMatch = IsFinishMatch(isCanBattle)      # 11

    if isStartApply == None and isFinishLeague == None :
        no = -3
    elif isFiveMem==None and isFiveLink==None and isLeader==None and isInGroup==None and isStartApply!=None and isFullLeague==None and isCompleteJoin==None and isEndApply==None and isRunMathMaker==None and isFinishLeague == None :
        no = -2
    elif (isFiveMem == None or  isFiveLink==None) and isLeader!=None and isInGroup!=None and isStartApply!=None and isFullLeague==None and isCompleteJoin==None and isEndApply==None and isRunMathMaker==None and isFinishLeague == None :
        no = -1
    elif isFiveMem!=None and isFiveLink!=None and isLeader!=None and isInGroup!=None and isStartApply!=None and isFullLeague==None and isCompleteJoin==None and isEndApply==None and isRunMathMaker==None and isFinishLeague == None :
        no = 0
    elif isStartApply!=None and isCompleteJoin!=None and isRunMathMaker==None:
        no = 1
    elif isCompleteJoin!=None and isRunMathMaker!=None and isCanBattle==None:
        no = 2
    elif isCanBattle!=None and isFinishMatch==None:
        no = 3
    elif isStart1stMatch!=None and isFinishLeague == None :
        no = 4
    elif isFinishLeague != None :
        no = 5
    else :
        no = "Pass All"

    return {
        "no":no,
        "isFiveMem":isFiveMem,
        "isFiveLink":isFiveLink,
        "isLeader":isLeader,
        "isInGroup":isInGroup,
        "isHost":isHost,
        "isStartApply":isStartApply,
        "isFullLeague":isFullLeague,
        "isStart1stMatch":isStart1stMatch,
        "isCompleteJoin":isCompleteJoin,
        "isRunMathMaker":isRunMathMaker,
        "isCanBattle":isCanBattle,
        "isFinishMatch":isFinishMatch,
        "canMatchMaker":canMatchMaker,
        "nowRound":nowRound
    }

def IsFiveMem(user):
    group = user.get_profile().get_group()
    if group :
        gm = group.get_member()
        if gm :
            return gm.count()
    return None

def IsFiveLink(league, user):
    group = user.get_profile().get_group()
    if group :
        gm = group.get_member()
        gl = GameLink.objects.filter(user__contains=gm.values_list('user', flat=True),game=league.game)
        if gl :
            if gl.count() >= 5 :
                return gl.count()
    return None

def IsLeader(user):
    group = user.get_profile().get_group()
    if group :
        if group.leader == user :
            return group.leader
    return None

def IsInGroup(user):
    group = user.get_profile().get_group()
    if group :
        return group
    return None

def IsHost(league,user):
    host = league.host
    if host == user :
        return host == user
    return None

def IsStartApply(league):
    now = timezone.localtime(timezone.now())
    if league.start_apply <= now :
        return league.start_apply
    return None

def IsFullLeague(league):
    lt = LeagueTeam.objects.filter(round__league=league, round__round=1)
    if lt:
        if lt.count() >= league.max_team :
            return lt.count()
    return None

def IsEndApply(league):
    now = timezone.localtime(timezone.now())
    if league.end_apply < now :
        return league.end_apply
    return None

def IsFinishLeague(league):
    lr = LeagueRound.objects.filter(league=league).order_by("-round")
    if lr :
        lm = LeagueMatch.objects.filter(Q(team_a__round=lr[0])|Q(team_b__round=lr[0])).order_by("-id")
        if lm :
            lastLM = lm[0]
            if lastLM.state == 10 :
                return lastLM
    return None

def IsStart1stMatch(league):
    lm = LeagueMatch.objects.filter(team_a__round__league=league, team_a__round__round=1)
    if lm :
        return lm[0]
    return None

def NowRound(league):
    lr = LeagueRound.objects.filter(league=league,is_finish=0).order_by("id")
    if lr :
        return lr[0]
    return None

def CanMatchMaker(nowRound):
    lm = LeagueMatch.objects.filter(Q(team_a__round=nowRound)|Q(team_b__round=nowRound))
    if lm :
        return None
    return nowRound

def IsCompleteJoin(league, user):
    group = user.get_profile().get_group()
    if group :
        lt = LeagueTeam.objects.filter(group=group, round__league=league).order_by("-id")
        if lt :
            return lt[0]
    return None

def IsRunMathMaker(lt):
    if lt :
        lm = LeagueMatch.objects.filter(Q(team_a=lt)|Q(team_b=lt))
        if lm :
            return lm[0]
    return None

def IsCanBattle(lm):
    now = timezone.localtime(timezone.now())
    if lm :
        if lm.date_match-timedelta(minutes=30) <= now :
            return lm
    return None

def IsFinishMatch(lm):
    if lm :
        if lm.state == 10 :
            return lm
    return None
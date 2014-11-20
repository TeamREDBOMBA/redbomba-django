# -*- coding: utf-8 -*-

# Create your views here.
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

    lastRound = LastRound(league)

    hasFiveMem = HasFiveMem(user)
    hasFiveLink = HasFiveLink(league,user)
    isLeader = IsLeader(user)
    hasGroup = HasGroup(user)
    isHost = IsHost(league,user)

    startApply = StartApply(league)
    completeJoin = CompleteJoin(lastRound, user)
    endApply = EndApply(league)
    noticeSchedule = NoticeSchedule(league,user)
    canBattle = CanBattle(league,user)
    isFinishGame = IsFinishGame(league,user)
    isFinishMatch = IsFinishMatch(league,user)
    isLast = IsLast(league,user)

    allFinish = AllFinish(league,lastRound)

    if allFinish == True :
        no = 5
    elif completeJoin==False:
        if endApply==True :
            no = 4
    elif canBattle==True and isFinishGame==False:
        if endApply==True or noticeSchedule == True :
            no = 3
    elif noticeSchedule==True and canBattle==False:
        if endApply==True or noticeSchedule == True :
            no = 2
    elif completeJoin==True and noticeSchedule==False:
        no = 1
    elif hasFiveMem==True and hasFiveLink==True and isLeader==True and hasGroup==True and startApply==True :
        no = 0
    elif isLeader==True and hasGroup==True and startApply==True :
        if hasFiveMem==False or hasFiveLink==False :
            no = -1
    elif isLeader==False and hasGroup==False and startApply==True :
        no = -2

    return {
        "no":no,
        "user":user,
        "league":league,
        "HasFiveMem":HasFiveMem(user,True),
        "HasFiveLink":HasFiveLink(league,user,True),
        "IsLeader":IsLeader(user,True),
        "HasGroup":HasGroup(user,True),
        "IsHost":IsHost(league, user,True),
        "StartApply":StartApply(league,True),
        "CompleteJoin":CompleteJoin(league, user,True),
        "EndApply":EndApply(league,True),
        "NoticeSchedule":NoticeSchedule(league,user,True),
        "CanBattle":CanBattle(league,user,True),
        "IsFinishGame":IsFinishGame(league,user,True),
        "IsFinishMatch":IsFinishMatch(league,user,True),
        "IsLast":IsLast(league,user,True),
        "lastRound":lastRound
        }

def HasFiveMem(user, req=False):
    if user:
        group = user.get_profile().get_group()
        if group :
            gm = group.get_member()
            if gm :
                if req :
                    return gm.count()
                if gm.count() >= 5 :
                    return True
    return False

def HasFiveLink(league,user,req=False):
    if user:
        group = user.get_profile().get_group()
        if group :
            gm = group.get_member()
            gl = GameLink.objects.filter(user__contains=gm.values_list('user', flat=True),game=league.game)
            if gl :
                if req :
                    return gl.count()
                if gl.count() >= 5 :
                    return True
    return False

def IsLeader(user,req=False):
    if user:
        group = user.get_profile().get_group()
        if group :
            return group.leader == user
    return False

def HasGroup(user,req=False):
    if user:
        group = user.get_profile().get_group()
        if group :
            return True
    return False

def IsHost(league,user,req=False):
    host = league.host
    return host == user

def StartApply(league,req=False):
    now = timezone.localtime(timezone.now())
    if league.start_apply <= now :
        return True
    return False

def CompleteJoin(lastRound,user,req=False):
    lt = LeagueTeam.objects.filter(round=lastRound,group=user.get_profile().get_group()).order_by("-id")
    if lt :
        if req :
            return lt[0]
        return True
    return False

def EndApply(league,req=False):

    now = timezone.localtime(timezone.now())
    if league.end_apply < now :
        return True
    return False

def NoticeSchedule(league,user,req=False):
    lr = get_or_none(LeagueRound,league=league,is_finish=0)
    lt = LeagueTeam.objects.filter(round=lr,group=user.get_profile().get_group()).order_by("-id")
    if lt:
        lm = LeagueMatch.objects.filter(Q(team_a=lt[0])|Q(team_b=lt[0])).order_by("-id")
        if lm :
            if req :
                return lm[0]
            return True
    return False

def CanBattle(league,user,req=False):
    now = timezone.localtime(timezone.now())
    lt = LeagueTeam.objects.filter(round__league=league,group=user.get_profile().get_group(),round__is_finish=1).order_by("-id")
    if lt :
        lm = LeagueMatch.objects.filter(Q(team_a=lt[0])|Q(team_b=lt[0])).order_by("-id")
        if lm :
            return lm[0].date_match-timedelta(minutes=30) <= now
    return False

def IsFinishGame(league,user,req=False):
    lt = LeagueTeam.objects.filter(round__league=league,group=user.get_profile().get_group(),round__is_finish=1).order_by("-id")
    if lt :
        lm = LeagueMatch.objects.filter(Q(team_a=lt[0])|Q(team_b=lt[0])).filter(state='10').order_by("-id")
        if lm :
            if req :
                return lm[0]
            return True
    return False

def IsFinishMatch(league,user,req=False):
    lt = LeagueTeam.objects.filter(round__league=league,group=user.get_profile().get_group(),round__is_finish=1).order_by("-id")
    if lt :
        lm = LeagueMatch.objects.filter(Q(team_a=lt[0])|Q(team_b=lt[0])).filter(state='10').order_by("-id")
        if lm :
            if lm.count() == int(lt[0].round.bestof) :
                if req :
                    return lm[0]
                return True
    return False

def IsLast(league,user,req=False):
    lt = LeagueTeam.objects.filter(round__league=league,group=user.get_profile().get_group(),round__is_finish=1).order_by("-id")
    if lt :
        lm = LeagueMatch.objects.filter(team_a__round=lt[0].round)
        if lm:
            if req :
                return lm[0]
            return lm.count() == 1
    return False

def LastRound(league):
    try:
        lastRound = LeagueRound.objects.filter(league=league,is_finish=0).order_by("id")[0]
    except Exception as e:
        lastRound = LeagueRound.objects.filter(league=league,is_finish=1).order_by("-id")[0]
    return lastRound

def AllFinish(league,lastRound):
    lm = get_or_none(LeagueMatch,team_a__round=lastRound)
    if lm :
        return lm.state == 10
    return False
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
        try:
            uid = request.user
            gid = GroupMember.objects.get(user=uid).group
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
    state = {}
    lr = LeagueRound.objects.filter(league=league).order_by("round")

    user_gid = get_or_none(GroupMember,user=user)
    if user_gid :
        user_gid = user_gid.group

    if get_or_none(Group,leader=user) :
        isAdmin = 1
    else :
        isAdmin = 0

    try:
        if LeagueTeam.objects.filter(group=user_gid,round__in=lr,is_complete=1).order_by("-round")[0].round.round != 1 :
            last_lt = LeagueTeam.objects.filter(group=user_gid,round__in=lr,is_complete=1).order_by("-round")[1]
            last_lm = LeagueMatch.objects.filter(Q(team_a=last_lt)|Q(team_b=last_lt)).order_by("-game")[0]
        else :
            last_lt = LeagueTeam.objects.filter(group=user_gid,round__in=lr,is_complete=1).order_by("-round")[0]
            last_lm = LeagueMatch.objects.filter(Q(team_a=last_lt)|Q(team_b=last_lt)).order_by("-game")[0]
    except Exception as e:
        last_lm = None

    try:
        last_round = lr.order_by("-round")
        if LeagueMatch.objects.filter(team_a__round=last_round[0]).order_by("-game")[0].state == 10 :
            final = LeagueMatch.objects.filter(team_a__round=last_round[0]).order_by("-game")[0]
            semifinal = LeagueMatch.objects.filter(team_a__in=LeagueTeam.objects.filter(round=last_round[1],is_complete=1)).order_by("-game")[0]
            if final.result == 'A':
                win_1 = final.team_a.group
                win_2 = final.team_b.group
            else:
                win_2 = final.team_a.group
                win_1 = final.team_b.group
            if semifinal[0].result == 'A':
                win_3_1 = semifinal[0].team_b.group
            else :
                win_3_1 = semifinal[0].team_a.group
            if semifinal[1].result == 'A':
                win_3_2 = semifinal[1].team_b.group
            else :
                win_3_2 = semifinal[1].team_a.group
            state = {"no":5,"win_1":win_1,"win_2":win_2,"win_3_1":win_3_1,"win_3_2":win_3_2,"last_lm":last_lm,"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league}
            return state
    except Exception as e:
        pass

    try:
        all1_lt = LeagueTeam.objects.filter(round=lr[1],round__league=league,is_complete=1)
        now = timezone.localtime(timezone.now())
        if all1_lt.count():
            all2_lt = LeagueTeam.objects.filter(id__in=all1_lt,group=user_gid,is_complete=1)
            if all2_lt.count() == 0:
                state = {"no":4,"last_lm":last_lm,"lr":all1_lt[0].round,"lt":all1_lt.filter(group=user_gid)[0],"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league,"zz":1}
                return state
        elif LeagueTeam.objects.filter(round=lr[0],group=user_gid,round__league=league,is_complete=1).count() == 0 and lr[0].league_id.end_apply < now :
            state = {"no":4,"last_lm":last_lm,"lr":lr[0],"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league,"zz":2}
            return state
    except Exception as e:
        state = {"no":4,"last_lm":last_lm,"lr":lr[0],"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league,"zz":3,"e":e.message}
        return state

    try:
        lt = LeagueTeam.objects.filter(group=user_gid,round__in=lr).order_by("-round")[0]
    except Exception as e:
        try:
            groupmem = GroupMember.objects.filter(group=user_gid,is_active=1).count()
        except Exception as e:
            groupmem = 0
        try:
            gamelink = GameLink.objects.filter(user__in=GroupMember.objects.filter(group=user_gid,is_active=1).values_list('user', flat=True)).count()
        except Exception as e:
            gamelink = 0
        if isAdmin == 0 or gamelink < 5 :
            if groupmem < 5 :
                state = {"no":-1,"e":e.message,"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league,"lr":lr[0],"groupmem":groupmem, "gamelink":gamelink}
            else :
                state = {"no":-2,"e":e.message,"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league,"lr":lr[0],"groupmem":groupmem, "gamelink":gamelink}
            return state
        state = {"no":0,"e":e.message,"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league,"lr":lr[0],"groupmem":groupmem, "gamelink":gamelink}
        return state

    try:
        lm = LeagueMatch.objects.filter(Q(team_a=lt)|Q(team_b=lt)).order_by("-game")[0]
    except Exception as e:
        state = {"no":1,"lt":lt,"last_lm":last_lm,"e":e.message,"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league}
        return state

    try:
        now = timezone.localtime(timezone.now()) + timedelta(minutes=30)
        lm = LeagueMatch.objects.filter(id=lm.id,date_match__lte=now).order_by("-game")[0]
    except Exception as e:
        state = {"no":2,"lm":lm,"last_lm":last_lm,"e":e.message,"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league}
        return state

    try:
        lm = LeagueMatch.objects.filter(Q(id=lm.id)&Q(state="10")).order_by("-game")[0]
        if lm.result == 'A' and lm.team_a.group_id == user_gid :
            next_lt = LeagueTeam.objects.get(Q(group=user_gid)&Q(round_round=lm.team_a.round.round+1)&Q(is_complete=1))
        elif lm.result == 'B' and lm.team_b.group_id == user_gid :
            next_lt = LeagueTeam.objects.get(Q(group=user_gid)&Q(round_round=lm.team_a.round.round+1)&Q(is_complete=1))
        else :
            return {"no":4,"last_lm":last_lm,"lr":lr[0],"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league}
    except Exception as e:
        state = {"no":3,"lm":lm,"last_lm":last_lm,"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league}
        return state

    last_lt = LeagueTeam.objects.filter(group=user_gid,round__in=lr,is_complete=1).order_by("-round")[0]
    last_lm = LeagueMatch.objects.filter(Q(team_a=last_lt)|Q(team_b=last_lt)).order_by("-game")[0]

    last_round = lr.order_by("-round")
    final = lm
    semifinal = LeagueMatch.objects.filter(team_a__in=LeagueTeam.objects.filter(round=last_round[1],is_complete=1)).order_by("-game")[0]
    if final.result == 'A':
        win_1 = final.team_a.group
        win_2 = final.team_b.group
    else:
        win_2 = final.team_a.group
        win_1 = final.team_b.group
    if semifinal[0].result == 'A':
        win_3_1 = semifinal[0].team_b.group
    else :
        win_3_1 = semifinal[0].team_a.group
    if semifinal[1].result == 'A':
        win_3_2 = semifinal[1].team_b.group
    else :
        win_3_2 = semifinal[1].team_a.group

    state = {"no":5,"win_1":win_1,"win_2":win_2,"win_3_1":win_3_1,"win_3_2":win_3_2,"last_lm":last_lm,"isAdmin":isAdmin,"user":user,"user_gid":user_gid,"league":league,"last_round":last_round}
    return state

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
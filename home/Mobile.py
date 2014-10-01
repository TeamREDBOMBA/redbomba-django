# -*- coding: utf-8 -*-

# Create your views here.
from redbomba.home.Func import *
import json
import datetime
from redbomba.home.models import GroupMember
from redbomba.home.models import GameLink
from redbomba.home.models import Notification
from redbomba.home.models import Chatting
from redbomba.home.models import League
from redbomba.home.models import Contents
from redbomba.home.models import LeagueReward
from redbomba.home.models import LeagueMatch
from redbomba.home.models import LeagueTeam
from redbomba.home.models import LeagueRound
from redbomba.home.models import UserProfile
from redbomba.home.Func import *
from redbomba.home.models import Group
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.dateformat import format
from django.views.decorators.csrf import csrf_exempt

######################################## Views ########################################

def mode1(request):
    try:
        email = request.GET["email"]
        password = request.GET["password"]
        username = get_user(email)
        if username is None:
            return HttpResponse('0')
        else :
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    state = []
                    state.append({"uid":user.id});
                    return HttpResponse(json.dumps(state), content_type="application/json")
                else:
                    return HttpResponse('0')
            else:
                return HttpResponse('0')
    except Exception as e:
        return HttpResponse(e.message)
    return HttpResponse('0')

def mode2(request) :
    try:
        state = []
        user = User.objects.get(id=request.GET["uid"])
        try:
            gl = GameLink.objects.get(uid=user).name
        except Exception as e:
            gl = None
        try:
            gm = GroupMember.objects.get(uid=user)
            state.append({"username":user.username, "user_icon":user.get_profile().user_icon, "gamelink":gl,"gid":gm.gid.id,"groupname":gm.gid.name,"groupimg":gm.gid.group_icon});
        except Exception as e:
            gm = None
            state.append({"username":user.username, "user_icon":user.get_profile().user_icon, "gamelink":gl,"gid":0,"groupname":0,"groupimg":0});
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getGroupListForMobile(request):
    state = []
    memlist = []
    user = User.objects.get(id=request.GET.get("uid",0))
    group = get_or_none(GroupMember,uid=user)
    gms = GroupMember.objects.filter(gid=group.gid).order_by("order")
    if group :
        for gm in gms :
            memlist.append({"uid":gm.uid.id,"username":gm.uid.username, "user_icon":gm.uid.get_profile().user_icon})
        state.append({"gid":group.gid.id,"name":group.gid.name,"nick":group.gid.nick,"uid":group.gid.uid.id,"icon":group.gid.group_icon,"game":group.gid.game.name,"memlist":memlist})
    return HttpResponse(json.dumps(state), content_type="application/json")

def getNotification(request):
    try:
        user = User.objects.get(id=request.GET["uid"])
        noti = Notification.objects.filter(uid=user)
        state = []
        now = format(timezone.localtime(timezone.now()), u'U')
        for n in noti :
            unixtime = format(n.date_updated, u'U')
            ret = NotificationMsg(n,user)
            state.append({"no":n.id,"action":n.action,"con":ret["con"],"img":ret["img"],"imgurl":ret["imgurl"],"date_updated":unixtime, "now":now, "time":n.get_time_diff()})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def NotificationDel(request):
    try:
        state = []
        Notification.objects.get(id=request.GET["no"]).delete()
        state.append({"result":1})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getMobileChatting(request):
    if request.user :
        state = []
        len = int(request.GET.get("len",0))
        group = get_or_none(Group,id=request.GET.get("gid"))
        msgs = list(Chatting.objects.filter(gid=group).order_by("date_updated"))
        for msg in msgs[-len:] :
            state.append({"id":msg.id,"uid":msg.uid.id,"username":msg.uid.username,"usericon":msg.uid.get_profile().user_icon,"con":msg.con})
        return HttpResponse(json.dumps(state), content_type="application/json")
    return HttpResponse('ERROR')

#League information for mobile
def getLeaugeInfo(request):
    state = []
    try:
        lgs = League.objects.filter(game_id="1")  # 추후 game_id 를 request.GET 해야함
        for lg in lgs:
            poster = Contents.objects.get(uto=lg.id, utotype="l", ctype="img")
            descrip = Contents.objects.get(uto=lg.id, utotype="l", ctype="txt")
            hosticon = UserProfile.objects.get(user_id=lg.uid_id)
            hostname = User.objects.get(id=lg.uid_id)
            firstroundid = LeagueRound.objects.get(league_id_id=lg.id, round=1)
            state.append({"id": lg.id, "name": lg.name,
                          "game_id": lg.game_id, "uid_d": lg.uid_id,
                          "level": lg.level, "method": lg.method,
                          "start_apply": str(lg.start_apply), "end_apply": str(lg.end_apply),
                          "min_team": lg.min_team, "max_team": lg.max_team,
                          "date_updated": str(lg.date_updated), "poster": poster.con, "descrip": descrip.con,
                          "hosticon": hosticon.user_icon, "hostname": hostname.username, "firstround": firstroundid.id})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getReward(request):
    state = []
    lid = request.GET["lid"]
    try:
        rewards = LeagueReward.objects.filter(league_id_id=lid)
        for r in rewards:
            state.append({"id": r.id, "league_id_id": r.league_id_id, "name": r.name, "con": r.con})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

# def getLeaguePoster(request):
#     state = []
#     try:
#         lps = Contents.objects.filter(utotype="l", ctype="img")
#         for lp in lps:
#             state.append({"id": lp.id, "uto": lp.uto, "utotype": lp.utotype, "ctype": lp.ctype, "con": lp.con})
#         return HttpResponse(json.dumps(state), content_type="application/json")
#     except Exception as e:
#         return HttpResponse(e.message)

def getLeagueTeam(request):
    state = []
    rid = request.GET["id"]
    try:
        teams = LeagueTeam.objects.filter(round_id=rid)
        for team in teams:
            group = Group.objects.get(id=team.group_id_id)
            state.append({"id": team.id, "group_id_id": team.group_id_id,
                            "round": team.round_id, "feasible_time": team.feasible_time,
                            "date_updated": str(team.date_updated), "groupicon": group.group_icon, "gname": group.name})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getLeagueRound(request):
    state = []
    lidid = request.GET["id"]
    try:
        lrounds = LeagueRound.objects.filter(league_id_id=lidid, round=1)
        for lround in lrounds:
            state.append({"id": lround.id, "league_id_id": lround.league_id_id,
                        "round": lround.round, "start": str(lround.start),
                        "end": str(lround.end), "bestof": lround.bestof, "is_finish": lround.is_finish})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getArenaTicket(request):
    state = []
    # league = request.GET["league"]
    usrid = request.GET["id"]
    try:
        # user = GroupMember.objects.get(uid_id=usrid)
        # state.append(Func.LeagueState(league, usrid))
        # state.append(Func.LeagueState(10, usrid))
        groupmember = GroupMember.objects.get(uid_id=usrid)
        group = Group.objects.get(id=groupmember.gid_id)
        leagueteam = LeagueTeam.objects.get(group_id_id=group.id)
        leagueround = LeagueRound.objects.get(id=leagueteam.round_id)
        league = League.objects.get(id=leagueround.league_id_id)

        state.append({"league_name": league.name, "group": group.name, "round": leagueround.round})
        # state.append(LeagueState(league, user))
        # state = Func.LeagueState(league, usrid)
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getRule(request):
    state=[]
    leagueid = request.GET["id"]
    try:
        rule = Contents.objects.get(uto=leagueid, ctype="inf", utotype="l")

        state.append({"id": rule.id, "rule": rule.con})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getSimpleLeagueInfo(request):
    state=[]
    try:
        lgs = League.objects.filter(game_id="1")  # 추후 game_id 를 request.GET 해야함
        for lg in lgs:
            poster = Contents.objects.get(uto=lg.id, utotype="l", ctype="img")
            lrounds = LeagueRound.objects.get(league_id_id=lg.id, round=1)
            now_team = LeagueTeam.objects.filter(round_id=lrounds.id)
            state.append({"id": lg.id, "name": lg.name,
                          "game_id": lg.game_id,
                          "start_apply": str(lg.start_apply), "end_apply": str(lg.end_apply),
                          "min_team": lg.min_team, "max_team": lg.max_team, "now_team": len(now_team),
                          "poster": poster.con})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getDetailLeagueInfo(request):
    state=[]
    leagueid = request.GET["id"]
    try:
        lg = League.objects.get(game_id="1", id=leagueid)  # 추후 game_id 를 request.GET 해야함
        poster = Contents.objects.get(uto=lg.id, utotype="l", ctype="img")
        descrip = Contents.objects.get(uto=lg.id, utotype="l", ctype="txt")
        hosticon = UserProfile.objects.get(user_id=lg.uid_id)
        hostname = User.objects.get(id=lg.uid_id)
        firstroundid = LeagueRound.objects.get(league_id_id=lg.id, round=1)
        now_team = LeagueTeam.objects.filter(round_id=firstroundid.id)
        state.append({"id": lg.id, "name": lg.name,
                      "game_id": lg.game_id, "uid_d": lg.uid_id,
                      "level": lg.level, "method": lg.method,
                      "start_apply": str(lg.start_apply), "end_apply": str(lg.end_apply),
                      "min_team": lg.min_team, "max_team": lg.max_team, "now_team": len(now_team),
                      "date_updated": str(lg.date_updated), "poster": poster.con, "descrip": descrip.con,
                      "hosticon": hosticon.user_icon, "hostname": hostname.username, "firstround": firstroundid.id})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

@csrf_exempt
def fromMobile(request):
    if 'mode' in request.GET:
        if request.GET["mode"] == "1":
            return mode1(request)
        elif request.GET["mode"] == "2":
            return mode2(request)
        elif request.GET["mode"] == "getGroupList" :
            return getGroupListForMobile(request)
        elif request.GET["mode"] == "Notification" :
            return getNotification(request)
        elif request.GET["mode"] == "NotificationDel" :
            return NotificationDel(request)
        elif request.GET["mode"] == "getChatting" :
            return getMobileChatting(request)
        elif request.GET["mode"] == "getLeagueInfo":
            return getLeaugeInfo(request)
        # elif request.GET["mode"] == "getLeaguePoster":
        #     return getLeaguePoster(request)
        elif request.GET["mode"] == "getReward":
            return getReward(request)
        elif request.GET["mode"] == "getLeagueTeam":
            return getLeagueTeam(request)
        elif request.GET["mode"] == "getLeagueRound":
            return getLeagueRound(request)
        elif request.GET["mode"] == "getArenaTicket":
            return getArenaTicket(request)
        elif request.GET["mode"] == "getRule":
            return getRule(request)
        elif request.GET["mode"] == "getSimpleLeagueInfo":
            return getSimpleLeagueInfo(request)
        elif request.GET["mode"] == "getDetailLeagueInfo":
            return getDetailLeagueInfo(request)

        return HttpResponse('0')
    else:
        return HttpResponse('0')
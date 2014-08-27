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
# from redbomba.home.models import Contents
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
            ret = NotificationMsg(n,GroupMember.objects.filter(uid=user)[0])
            state.append({"no":n.id,"tablename":n.tablename,"con":ret["con"],"img":ret["img"],"imgurl":ret["imgurl"],"date_updated":unixtime, "now":now, "time":n.get_time_diff()})
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
        lgs = League.objects.filter(game_id="1")
        for lg in lgs:
            # poster = Contents.objects.get(uto=lg.id, utotype="l", ctype="img")
            state.append({"id": lg.id, "name": lg.name,
                          "game_id": lg.game_id, "uid_d": lg.uid_id,
                          "level": lg.level, "method": lg.method,
                          "start_apply": str(lg.start_apply), "end_apply": str(lg.end_apply),
                          "min_team": lg.min_team, "max_team": lg.max_team,
                          "date_updated": str(lg.date_updated)})
            # , "poster": poster})
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
        return HttpResponse('0')
    else:
        return HttpResponse('0')
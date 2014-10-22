# -*- coding: utf-8 -*-

# Create your views here.
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
from redbomba.home.models import Feed
from redbomba.home.models import Group
from redbomba.home.models import FeedReply
from redbomba.home.models import FeedContents
from redbomba.home.models import PrivateCard
from redbomba.home.Func import *
from redbomba.home.Feed import *
from redbomba.home.Arena_league import *
from django.conf.global_settings import DEFAULT_CONTENT_TYPE
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.dateformat import format
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

######################################## Views ########################################

def get_date_format(date_updated):
    now = datetime.utcnow().replace(tzinfo=utc)
    date_date = ""
    timediff = now - date_updated
    timediff = timediff.total_seconds()
    if timediff > 259200:
        date_date = date_updated.strftime('%m.%d')
    elif timediff > 86400:
        date_date = str(int(timediff/3600/24))+"일 전"
    elif timediff > 3600:
        date_date = str(int(timediff/3600))+"시간 전"
    elif timediff > 60:
        date_date = str(int(timediff/60))+"분 전"
    else :
        date_date = str(int(timediff))+"초 전"
    return date_date

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

        gl = get_or_none(GameLink,user=user)
        if gl :
            gl = gl.name

        gid, groupname, groupimg = 0, 0, 0

        gm = get_or_none(GroupMember,user=user)
        if gm :
            gid = gm.group.id
            groupname = gm.group.name
            groupimg = gm.group.group_icon

        state.append({"id":user.id,"username":user.username, "user_icon":user.get_profile().get_icon(), "gamelink":gl,"gid":gid,"groupname":groupname,"groupimg":groupimg})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getGroupListForMobile(request):
    state = []
    memlist = []
    user = User.objects.get(id=request.GET.get("uid",0))
    group = get_or_none(GroupMember,user=user)
    gms = GroupMember.objects.filter(group=group.group).order_by("order")
    if group :
        for gm in gms :
            memlist.append({"uid":gm.user.id,"username":gm.user.username, "user_icon":gm.user.get_profile().get_icon()})
        state.append({"gid":group.group.id,"name":group.group.name,"nick":group.group.nick,"uid":group.group.leader.id,"icon":group.group.group_icon,"game":group.group.game.name,"memlist":memlist})
    return HttpResponse(json.dumps(state), content_type="application/json")

def getGlobalListForMobile(request):
    now = datetime.utcnow().replace(tzinfo=utc)
    state = []
    globalfeed = GlobalCard.objects.filter().order_by("-date_updated")
    if globalfeed :
        for gf in globalfeed :
            comment_len = 0
            comment = Feed.objects.filter(uto=gf.id,utotype="g")
            if comment :
                comment_len = comment.count()
            state.append({"id":gf.id,"title":gf.title,"txt":gf.con,"img":"/media/%s"%(gf.src),"comment_no":comment_len,"user":gf.user.username,"date_updated":get_date_format(gf.date_updated)})
    return HttpResponse(json.dumps(state), content_type="application/json")

def getPrivateListForMobile(request):
    user = User.objects.get(id=request.GET.get("uid",0))
    state = []

    mygroup = GroupMember.objects.filter(user=user).values_list('group', flat=True)
    if mygroup :
        gm = GroupMember.objects.filter(Q(group__in=mygroup)&~Q(user=user))
        if gm :
            for value in gm :
                state.append({
                    'type':'groupmember',
                    'icon':"/media/group_icon/%s"%value.group.group_icon,
                    'name':value.group.name,
                    'con':"%s님이 %s에 새로운 멤버로 함류하였습니다.\n%s님의 도움의 손길과 따뜻한 환영의 메시지가 필요해 보이는 군요!"%(value.user.username,value.group.name,user.username),
                    'date_updated':get_date_format(value.date_updated),
                    'date':int(format(value.date_updated, u'U'))
                })

    feed = Feed.objects.filter(ufrom=user.id,ufromtype='u')
    reply = FeedReply.objects.filter(Q(feed__in=feed)&~Q(user=user)).order_by("-date_updated")
    uto = ""
    if reply :
        for value in reply :
            if value.feed.utotype == 'l' :
                uto = get_or_none(League, id=value.feed.uto).name
            state.append({
                'type':'reply',
                'icon':value.user.get_profile().get_icon(),
                'name':value.user.username,
                'con':'%s님이 %s에 올리신 "%s"글에 %s님의 댓글"%s"이 달렸습니다.\n지금 확인하세요!'%(user.username, uto, value.feed.get_con().con,value.user.username,value.con),
                'date_updated':get_date_format(value.date_updated),
                'date':int(format(value.date_updated, u'U'))
            })

    pc = PrivateCard.objects.filter(user=user).order_by("-date_updated")
    if pc :
        for value in pc :
            state.append({
                'type':'system',
                'icon':"/media/icon/redbomba.png",
                'name':"REDBOMBA",
                'con':"%s님. 만나서 반가워요!\n이 곳은 %s님에게 관련된 소식만을 모아서 보여주는 활동 스트림 영역입니다.\n레드밤바에서 다양한 활동을 즐겨보세요!"%(value.user.username,value.user.username),
                'date_updated':get_date_format(value.date_updated),
                'date':int(format(value.date_updated, u'U'))
            })

    state.sort(key=lambda item:item['date'], reverse=True)

    return HttpResponse(json.dumps(state), content_type="application/json")

def getNotification(request):
    try:
        user = User.objects.get(id=request.GET["uid"])
        noti = Notification.objects.filter(user=user)
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
        msgs = list(Chatting.objects.filter(group=group).order_by("date_updated"))
        for msg in msgs[-len:] :
            state.append({"id":msg.id,"uid":msg.user.id,"username":msg.user.username,"usericon":msg.user.get_profile().get_icon(),"con":msg.con})
        return HttpResponse(json.dumps(state), content_type="application/json")
    return HttpResponse('ERROR')

#League information for mobile
def getReward(request):
    state = []
    lid = request.GET["lid"]
    try:
        rewards = LeagueReward.objects.filter(league_id=lid)
        for r in rewards:
            state.append({"id": r.id, "league_id_id": r.league_id, "name": r.name, "con": r.con})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getLeagueTeam(request):
    state = []
    rid = request.GET["id"]
    try:
        teams = LeagueTeam.objects.filter(round_id=rid)
        for team in teams:
            group = Group.objects.get(id=team.group_id)
            state.append({"id": team.id, "group_id_id": team.group_id,
                          "round": team.round_id, "feasible_time": team.feasible_time,
                          "date_updated": str(team.date_updated), "groupicon": group.group_icon, "gname": group.name})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getLeagueRound(request):
    state = []
    lid = request.GET["id"]
    try:
        lrounds = LeagueRound.objects.filter(league_id=lid)
        for lround in lrounds:
            state.append({"id": lround.id, "league_id_id": lround.league_id,
                          "round": lround.round, "start": str(lround.start),
                          "end": str(lround.end), "bestof": lround.bestof, "is_finish": lround.is_finish})
        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

# def getCurrentRound(request):
#     state = []
#     # date_date = ""
#     # timediff = now - date_updated
#     # timediff = timediff.total_seconds()
#     lid = request.GET["lid"]
#     try:
#         currentRound = LeagueRound.objects.filter(league_id=lid).order_by("start")
#         for cr in currentRound:
#             now = datetime.utcnow().replace(tzinfo=utc)
#             if cr.start.replace(tzinfo=utc) > now:
#                 state.append({"start": cr.start, "end": cr.end})
#             return HttpResponse(json.dumps(state), content_type="application/json")
#     except Exception as e:
#         return HttpResponse(e.message)

def getArenaTicket(request):
    state = []
    usrid = request.GET["id"]
    try:
        groupmember = GroupMember.objects.get(user_id=usrid)
        group = Group.objects.get(id=groupmember.group_id)
        leagueteam = LeagueTeam.objects.filter(group_id=group.id)
        for lt in leagueteam:
            leagueround = LeagueRound.objects.get(id=lt.round_id)
            league = League.objects.get(id=leagueround.league_id)
            # userprofile = UserProfile.objects.get(user_id=usrid)
            s = LeagueState(league.id, usrid)
            leaguematch = LeagueMatch.objects.filter(Q(team_a_id=lt.id) | Q(team_b_id=lt.id)).order_by("date_updated")
            if (len(leaguematch) > 0):
                if (group.id == leaguematch[0].team_a_id):
                    opteam_num = leaguematch[0].team_b_id
                else:
                    opteam_num = leaguematch[0].team_a_id
                opteam = LeagueTeam.objects.get(id=opteam_num)
                opgroup = Group.objects.get(id=opteam.group_id)
                state.append({"league_name": league.name, "round": leagueround.round,
                              "group": group.name, "groupicon": group.group_icon,
                              "opgroup": opgroup.name, "opgroupicon": opgroup.group_icon,
                              "next_match": str(leaguematch[0].date_match), "state": s['no']})
            else:
                state.append({"league_name": league.name, "round": leagueround.round,
                              "group": group.name, "groupicon": group.group_icon,
                              "opgroup": "대전 상대가 아직 정해지지 않았습니다.", "opgroupicon": "",
                              "next_match": "0", "state": s['no']})
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
    # try:
    lgs = League.objects.filter()
    for lg in lgs:
        # poster = Contents.objects.get(uto=lg.id, utotype="l", ctype="img")
        lrounds = LeagueRound.objects.get(league=lg.id, round=1)
        now_team = LeagueTeam.objects.filter(round=lrounds.id)
        state.append({"id": lg.id, "name": lg.name,
                      "game_id": lg.game.name,
                      "start_apply": str(lg.start_apply), "end_apply": str(lg.end_apply),
                      "min_team": lg.min_team, "max_team": lg.max_team, "now_team": len(now_team),
                      "poster": str(lg.poster)})
    return HttpResponse(json.dumps(state), content_type="application/json")
    # except Exception as e:
    #     return HttpResponse(e.message)

def getDetailLeagueInfo(request):
    state = []
    lid = request.GET["id"]
    # try:
    lg = League.objects.get(id=lid)
    # poster = Contents.objects.get(uto=lg.id, utotype="l", ctype="img")
    # descrip = Contents.objects.get(uto=lg.id, utotype="l", ctype="txt")
    hostprofile = UserProfile.objects.get(user=lg.host_id)
    host = User.objects.get(id=lg.host_id)
    firstround = LeagueRound.objects.get(league_id=lg.id, round=1)
    now_team = LeagueTeam.objects.filter(round=firstround.id)
    state.append({"id": lg.id, "name": lg.name,
                  "game_id": lg.game_id, "host": lg.host_id,
                  "level": lg.level, "method": lg.method,
                  "start_apply": str(lg.start_apply), "end_apply": str(lg.end_apply),
                  "min_team": lg.min_team, "max_team": lg.max_team, "now_team": len(now_team),
                  "date_updated": str(lg.date_updated), "poster": str(lg.poster), "concept": lg.concept,
                  "hosticon": str(hostprofile.user_icon), "hostname": host.username, "firstround": firstround.id,
                  "frstart": str(firstround.start), "frend": str(firstround.end), "rule": lg.rule})
    return HttpResponse(json.dumps(state), content_type="application/json")
    # except Exception as e:
    #     return HttpResponse(e.message)

def getUserProfile(request):
    state = []
    uid = request.GET["id"]
    # try:
    user = User.objects.get(id=uid)
    userprofile = UserProfile.objects.get(user=uid)
    groupmember = GroupMember.objects.get(user_id=uid)
    group = Group.objects.get(id=groupmember.group_id)
    numberofmembers = GroupMember.objects.filter(group_id=groupmember.group_id)

    state.append({"usericon": str(userprofile.user_icon), "username": user.username, "email": user.email,
                  "groupicon": group.group_icon, "groupname": group.name, "groupini": group.nick,
                  "gameid": group.game.name, "numofmem": len(numberofmembers)})

    return HttpResponse(json.dumps(state), content_type="application/json")
    # except Exception as e:
    #     return HttpResponse(e.message)

def getLinkedGames(request):
    state = []
    uid = request.GET["id"]
    try:
        gamelink = GameLink.objects.filter(user_id=uid)

        for gl in gamelink:
            state.append({"gameid": gl.game_id, "userid": gl.name})

        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def getLeagueFeed(request):
    state = []
    lid = request.GET["lid"]
    # try:
    feeds = Feed.objects.filter(uto=lid, utotype="l").order_by("-date_updated")
    lg = League.objects.get(id=lid)
    for f in feeds:
        feedcontents = FeedContents.objects.get(feed=f.id, contype="txt")
        userprofile = UserProfile.objects.get(user=f.ufrom)
        user = User.objects.get(id=f.ufrom)
        groupmember = GroupMember.objects.get(user=f.ufrom)
        group = Group.objects.get(id=groupmember.group_id)
        reply = FeedReply.objects.filter(feed_id=f.id)
        state.append({"id": f.id, "con": feedcontents.con, "usericon": str(userprofile.user_icon),
                      "username": user.username, "groupname": group.name, "update": str(f.date_updated),
                      "host": lg.host_id, "user": user.id, "replynum": len(reply)})

    return HttpResponse(json.dumps(state), content_type="application/json")
    # except Exception as e:
    #     return HttpResponse(e.message)

def postLeagueFeed(request):
    # # state = []
    uid = request.POST.get("uid")
    uto = request.POST.get("uto")
    utotype = request.POST.get("utotype")
    feedtype = request.POST.get("feedtype")
    txt = request.POST.get("txt")
    tag = request.POST.get("tag")
    img = request.POST.get("img")
    vid = request.POST.get("vid")
    log = request.POST.get("log")
    hyp = request.POST.get("hyp")

    insertFeed(uid, uto, utotype, feedtype, tag, img, txt, vid, log, hyp)
    # pw = request.POST["pw"]
    # state.append({"id": id, "pw": pw})

def getFeedComments(request):
    state = []
    fid = request.GET["fid"]
    try:
        reply = FeedReply.objects.filter(feed_id=fid).order_by("-date_updated")
        for r in reply:
            # content = Contents.objects.get(utotype="r", uto=r.id)
            userprofile = UserProfile.objects.get(user_id=r.user_id)
            user = User.objects.get(id=r.user_id)

            state.append({"user_icon": str(userprofile.user_icon), "user_name": user.username,
                          "con": r.con, "update": str(r.date_updated)})

        return HttpResponse(json.dumps(state), content_type="application/json")
    except Exception as e:
        return HttpResponse(e.message)

def postFeedReply(request):
    uid = request.POST.get("uid")
    fid = request.POST.get("fid")
    txt = request.POST.get("txt")

    insertReply(uid, fid, txt)

def getCondition(request):
    state = []
    uid = request.GET["uid"]
    lid = request.GET["lid"]
    try:
        s = LeagueState(lid, uid)
        if s["user_gid"] == None:
            s["user_gid"] = "0"
        if s['no'] < 1:
            state.append({"no": s["no"], "isLeader": str(s["isAdmin"]), "group": str(s["user_gid"]),
                      "groupmem": str(s['groupmem']), "gamelink": str(s['gamelink'])})
        else:
            state.append({"no": s["no"], "isLeader": str(s["isAdmin"]), "group": str(s["user_gid"]),
                      "groupmem": "-1", "gamelink": "-1"})

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
        elif request.GET["mode"] == "getGlobalList" :
            return getGlobalListForMobile(request)
        elif request.GET["mode"] == "getPrivateList" :
            return getPrivateListForMobile(request)
        elif request.GET["mode"] == "Notification" :
            return getNotification(request)
        elif request.GET["mode"] == "NotificationDel" :
            return NotificationDel(request)
        elif request.GET["mode"] == "getChatting" :
            return getMobileChatting(request)
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
        elif request.GET["mode"] == "getUserProfile":
            return getUserProfile(request)
        elif request.GET["mode"] == "getLeagueFeed":
            return getLeagueFeed(request)
        elif request.GET["mode"] == "getLinkedGames":
            return getLinkedGames(request)
        elif request.GET["mode"] == "postLeagueFeed":
            return postLeagueFeed(request)
        elif request.GET["mode"] == "getFeedComments":
            return getFeedComments(request)
        elif request.GET["mode"] == "postFeedReply":
            return postFeedReply(request)
        elif request.GET["mode"] == "getCondition":
            return getCondition(request)
        elif request.GET["mode"] == "postLeagueTeam":
            return setLeagueteam(request)
        # elif request.GET["mode"] == "getCurrentRound":
        #     return getCurrentRound(request)

        return HttpResponse('0')
    else:
        return HttpResponse('0')
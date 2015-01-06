# -*- coding: utf-8 -*-

from datetime import datetime
import random
import ssl
import urllib
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.utils.timezone import utc
from sleekxmpp import ClientXMPP
from redbomba.arena.models import League, LeagueTeam
from redbomba.group.models import GroupMember, Group
from redbomba.head.models import Notification
from redbomba.home.models import get_or_none, Game, GameLink, get_json, iriToUri


def head_userinfo(request):
    val = ""
    if request.method=='POST':
        uid = request.user
        gid =get_or_none(GroupMember,user=uid)

        if uid : uid = uid.id
        else: uid = 0

        if gid : gid = gid.id
        else: gid = 0

        val = val + "<uid>%d</uid>" %(uid)
        val = val + "<gid>%d</gid>" %(gid)
    else:
        val = "POST ERROR"
    return HttpResponse(val)

def head_start(request):
    gl = GameLink.objects.filter(user=request.user)
    context = {
            'user': request.user,
            'gamelink':gl,
            'appname':'head'
        }
    return render(request, 'head_start.html', context)

def head_search(request) :
	users = []
	groups = []
	text = request.POST.get("text","")

	query_u = User.objects.filter(Q(username__icontains=text)|Q(id__in=GameLink.objects.filter(account_name__icontains=text).values_list('user', flat=True)))
	for val in query_u:
		gl = get_or_none(GameLink,user=val)
		gm = get_or_none(GroupMember,user=val)
		if gm : gm = gm.group
		users.append({'uid':val, 'gamelink':gl, 'group':gm})

	query_g = Group.objects.filter(Q(name__icontains=text)|Q(nick__icontains=text)|Q(leader__in=User.objects.filter(username__icontains=text)))
	for val in query_g:
		groups.append({'gid':val})

	context = {"users":users,"groups":groups}
	return render(request, 'head_search.html', context)

def head_notification(request) :
    notis = Notification.objects.filter(user=request.user)
    context = {"user":request.user,"notis":notis}
    return render(request, 'head_notification.html', context)

def head_field(request) :
    query_g = GroupMember.objects.filter(user=request.user)
    groups = []
    for val in query_g:
        groups.append(val.group)

    user = get_or_none(GroupMember,user=request.user)
    query_l = League.objects.filter(id__in=LeagueTeam.objects.filter(group=user.group).values_list('round__league', flat=True))
    leagues = []
    for val in query_l:
        leagues.append(val)
    context = {"groups":groups,"leagues":leagues}
    return render(request, 'head_field.html', context)

def head_gamelink(request):
    context = {
            'user': request.user
        }
    return render(request, 'head_gamelink.html', context)

def head_gamelink_list(request):
    query = request.GET.get("query")
    gamelist = []
    if query : games = Game.objects.filter(name__icontains=query,is_active=1)
    else : games = Game.objects.filter(is_active=1)
    for game in games :
        link = get_or_none(GameLink,user=request.user,game=game)
        gamelist.append({'game':game,'link':link})

    context = {
            'gamelist': gamelist,
        }
    return render(request, 'head_gamelink_list.html', context)

def head_gamelink_login(request):
    gid = request.GET.get("id")
    game = get_or_none(Game,id=int(gid))
    context = {
            'game': game
        }
    return render(request, 'head_gamelink_login.html', context)

def head_gamelink_link(request) :
    username = request.POST.get("id")
    password = request.POST.get("pw")
    game_id = request.POST.get("game_id")

    game = get_or_none(Game,id=game_id)

    if game and username and password :
        if game.name == 'League of Legends' :
            xmpp = ClientXMPP(username+'@pvp.net', 'AIR_'+password)
            xmpp.ssl_version = ssl.PROTOCOL_SSLv3
            xmpp.connect(address=("chat.kr.lol.riotgames.com", 5223), reattempt=False, use_tls=False, use_ssl=True)
            xmpp.process(block=False)
            try:
                roster = xmpp.get_roster().__str__()
                start = roster.index('sum')+3
                end = roster.index('@')
                sid = roster[start:end]
                xmpp.disconnect()
                insertGameLink(request.user, game, sid)
                return summoner(request,sid)
            except Exception as e:
                return HttpResponse("wrong id and password=%s"%e)
    return HttpResponse("wrong id and password")

def head_gamelink_delete(request):
    uid = request.user
    game = GameLink.objects.get(id=request.POST.get("gl"))
    game.delete()
    return HttpResponse("Done")

def head_gamelink_skip(request):
    profile = request.user.get_profile()
    profile.is_pass_gamelink = 1
    profile.save()
    return HttpResponseRedirect("/")

def head_gamelink_load(request) :
    account_id = request.POST.get("account_id")
    return summoner(request,account_id)

def reloadSummoner(request, sid, sinfo):
    gl = get_or_none(GameLink,account_id=sid)
    if gl :
        if gl.account_name != sinfo['name'] :
            gl.account_name = sinfo['name']
            gl.save()

def summoner(request,sid=None):
    gl = get_or_none(GameLink,account_id=sid)
    if gl :
        sid = gl.account_id

    apikey = [
        #"fa072bf3-4b01-4719-8036-e3c32c1fd108",
        "382f860d-58b6-420e-b769-049b36c6f862"
        #"1cb3ed80-344a-47e3-b03d-1344bde33f30"
    ]

    if sid :
        random.shuffle(apikey)
        json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v1.4/summoner/%s?api_key=%s' %(sid,apikey[0])))
        summoner_info = dict(json_res).values()[0]
        summoner_id = str(summoner_info['id'])
        user = summoner_info['name']
        reloadSummoner(request,sid,summoner_info)

        random.shuffle(apikey)
        try:
            json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v2.4/league/by-summoner/%s/entry?api_key=%s' %(summoner_id,apikey[0])))
            tier = json_res[summoner_id][0]['tier']
            rank = json_res[summoner_id][0]['entries'][0]['division']
            lp = json_res[summoner_id][0]['entries'][0]['leaguePoints']
        except Exception as e:
            tier = rank = lp = None

        random.shuffle(apikey)
        wins = losses = None
        try :
            json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v1.3/stats/by-summoner/%s/summary?season=SEASON4&api_key=%s' %(summoner_id,apikey[0])))

            for res in json_res['playerStatSummaries'] :
                if res['playerStatSummaryType'] == "RankedSolo5x5" :
                    wins = res['wins']
                    losses = res['losses']
                    break
        except Exception as e:
            wins = losses = None

        summoner_stat = {'tier':tier,'rank':rank,'lp':lp,'wins':wins,'losses':losses}

        summoner_most = []
        try:
            cham = BeautifulSoup(urllib.urlopen(iriToUri('http://www.op.gg/summoner/userName=%s' %(user)))).findAll('div', {'class': 'ChampionBox'})
            for i in range(0,3) :
                cham_res={
                    "img":cham[i].findAll('img')[0]['src'],
                    "name":cham[i].findAll('span', {'class': 'name'})[0].contents[0],
                    "kda":cham[i].findAll('span', {'class': 'kda'})[0].contents[0][:-2],
                    "played":cham[i].findAll('div', {'class': 'ChampionPlayed'})[0].findAll('span')[1].contents[0]
                }
                summoner_most.append(cham_res)
        except Exception as e:
            pass

        summoner_recent = []
        random.shuffle(apikey)
        json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v1.3/game/by-summoner/%s/recent?api_key=%s' %(summoner_info['id'],apikey[0])))['games']
        for res in json_res[0:8] :
            if setStatsValue(res, 'win') == True :
                win = "승"
            else :
                win = "패"
            try:
                kda = "%.2f"%((float(setStatsValue(res, 'championsKilled'))+float(setStatsValue(res, 'assists')))/float(setStatsValue(res, 'numDeaths')))
            except Exception as e:
                kda = "Perfect"
            if res['subType'] == "NONE" or res['subType'] == "CAP_5x5" or res['subType'] == "ONEFORALL_5x5" or res['subType'] == "ODIN_UNRANKED" or res['subType'] == "RANKED_PREMADE_3x3" or res['subType'] == "RANKED_PREMADE_5x5" :
                mathchtype = {"name":"커스텀","color":"#fff","bc":"#2c3e50"}
            elif res['subType'] == "NORMAL" or res['subType'] == "NORMAL_3x3" :
                mathchtype = {"name":"노말","color":"#fff","bc":"#7f8c8d"}
            elif res['subType'] == "BOT" or res['subType'] == "BOT_3x3" :
                mathchtype = {"name":"봇전","color":"#000","bc":"inherit"}
            elif res['subType'] == "RANKED_SOLO_5x5" :
                mathchtype = {"name":"솔랭","color":"#fff","bc":"#f39c12"}
            elif res['subType'] == "RANKED_TEAM_3x3" or res['subType'] == "RANKED_TEAM_5x5" :
                mathchtype = {"name":"팀랭","color":"#fff","bc":"#f39c12"}
            elif res['subType'] == "ARAM_UNRANKED_5x5":
                mathchtype = {"name":"아람","color":"#000","bc":"inherit"}
            else :
                mathchtype = {"name":"ETC","color":"#000","bc":"inherit"}

            summoner_recent.append({
                'win':win,
                'win_bool':setStatsValue(res, 'win'),
                'cid':res['championId'],
                'spell1':res['spell1'],
                'spell2':res['spell2'],
                'kill':setStatsValue(res, 'championsKilled'),
                'assists':setStatsValue(res, 'assists'),
                'death':setStatsValue(res, 'numDeaths'),
                'kda':kda,
                'item0':setStatsValue(res, 'item0'),
                'item1':setStatsValue(res, 'item1'),
                'item2':setStatsValue(res, 'item2'),
                'item3':setStatsValue(res, 'item3'),
                'item4':setStatsValue(res, 'item4'),
                'item5':setStatsValue(res, 'item5'),
                'mathchtype':mathchtype,
                'createdate':datetime.utcfromtimestamp(int(res['createDate'])/1000).replace(tzinfo=utc),
                'timePlayed':int(setStatsValue(res, 'timePlayed'))/60,
                'level':setStatsValue(res, 'level'),
                'cs':setStatsValue(res, 'neutralMinionsKilleds')+setStatsValue(res, 'minionsKilled')
            })

        isLinked = get_or_none(GameLink,account_name=summoner_info['name'])

        context = {
            'summoner_info':summoner_info,
            'summoner_stat':summoner_stat,
            'summoner_most':summoner_most,
            'summoner_recent':summoner_recent,
            'isLinked':isLinked,
            'uid' : request.user.id,
            'name':1,
            'from':request.GET.get('from')
        }

    else :
        context = {
            'uid' : request.user.id,
            'from':request.GET.get('from')
        }
    return render(request, 'head_gamelink_detail_lol.html', context)

def insertGameLink(uid=None, game=None, sid=None):
    if uid and game and sid :
        gl = GameLink.objects.filter(user=uid,game=game)
        if int(gl.count()) > 0 :
            gl = GameLink.objects.get(user=uid,game=game)
            gl.game = game
            gl.account_name = ""
            gl.account_id = sid
            gl.save()
        else:
            GameLink.objects.create(user=uid,game=game,account_name="",account_id=sid)

def setStatsValue(j, s):
    try:
        return j['stats'][s]
    except Exception as e:
        return 0

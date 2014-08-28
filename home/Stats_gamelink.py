# -*- coding: utf-8 -*-

# Create your views here.
import urllib
import random
from redbomba.home.Func import *
from redbomba.home.models import Game
from redbomba.home.models import GameLink
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils.timezone import utc
from django.shortcuts import render
from django.http import HttpResponseRedirect

######################################## Views ########################################

def reloadSummoner(request, name, sinfo):
    gl = get_or_none(GameLink,name=name)
    if gl :
        if gl.name != sinfo['name'] :
            gl.name = sinfo['name']
            gl.sid = sinfo['id']
            gl.save()
        elif gl.sid != sinfo['id'] :
            gl.name = sinfo['name']
            gl.sid = sinfo['id']
            gl.save()

def summoner(request):
    user = request.POST.get('user')
    sid = request.POST.get('sid')
    if user is None :
        sid = get_or_none(GameLink,name=sid)
        if sid :
            sid = sid.sid

    apikey = [
        #"fa072bf3-4b01-4719-8036-e3c32c1fd108",
        "382f860d-58b6-420e-b769-049b36c6f862"
        #"1cb3ed80-344a-47e3-b03d-1344bde33f30"
    ]

    if user or sid :
        if user :
            random.shuffle(apikey)
            json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v1.4/summoner/by-name/%s?api_key=%s' %(user,apikey[0])))
            summoner_info = dict(json_res).values()[0]
            summoner_id = str(summoner_info['id'])
            user = summoner_info['name']
            reloadSummoner(request,user,summoner_info)

        elif sid :
            random.shuffle(apikey)
            json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v1.4/summoner/%s?api_key=%s' %(sid,apikey[0])))
            summoner_info = dict(json_res).values()[0]
            summoner_id = str(summoner_info['id'])
            user = summoner_info['name']
            reloadSummoner(request,user,summoner_info)

        random.shuffle(apikey)
        json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v2.4/league/by-summoner/%s/entry?api_key=%s' %(summoner_id,apikey[0])))
        tier = json_res[summoner_id][0]['tier']
        rank = json_res[summoner_id][0]['entries'][0]['division']
        lp = json_res[summoner_id][0]['entries'][0]['leaguePoints']

        random.shuffle(apikey)
        json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v1.3/stats/by-summoner/%s/summary?season=SEASON4&api_key=%s' %(summoner_id,apikey[0])))

        for res in json_res['playerStatSummaries'] :
            if res['playerStatSummaryType'] == "RankedSolo5x5" :
                wins = res['wins']
                losses = res['losses']
                break
        summoner_stat = {'tier':tier,'rank':rank,'lp':lp,'wins':wins,'losses':losses}

        summoner_most = []
        try:
            cham = BeautifulSoup(urllib.urlopen(iriToUri('http://www.op.gg/summoner/userName=%s' %(user)))).findAll('div', {'class': 'ChampionBox'})
            for i in range(0,3) :
                cham_res={
                    "img":cham[i].findAll('img')[0]['src'],
                    "name":cham[i].findAll('span', {'class': 'name'})[0].contents[0],
                    "kda":cham[i].findAll('span', {'class': 'kda'})[0].contents[0][:-2],
                    "title":cham[i].findAll('span', {'class': 'title'})[0].contents[0]
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

        isLinked = get_or_none(GameLink,name=summoner_info['name'])

        context = {
            'summoner_info':summoner_info,
            'summoner_stat':summoner_stat,
            'summoner_most':summoner_most,
            'summoner_recent':summoner_recent,
            'isLinked':isLinked,
            'uid' : request.user.id,
            'name':1,
            'from':request.GET['from']
        }

    else :
        context = {
            'uid' : request.user.id,
            'from':request.GET['from']
        }
    return render(request, 'search_lol.html', context)

def write_GameLink(request):
    dfrom = request.POST.get("from")
    if request.POST.get("action") == "insert" :
        uid = request.user
        game = get_or_none(Game,name=request.POST.get("gid"))
        name = request.POST.get("name")
        sid = request.POST.get("sid")
        insertGameLink(uid, game, name, sid)
        return HttpResponseRedirect(dfrom)
    else :
        try :
            uid = request.user
            game = GameLink.objects.get(id=request.POST["gl"])
            game.delete()
            return HttpResponseRedirect(dfrom)
        except Exception as e:
            return HttpResponseRedirect(dfrom)

def insertGameLink(uid=None, game=None, name=None, sid=None):
    if uid and game and name and sid :
        gl = GameLink.objects.filter(uid=uid,game=game)
        if int(gl.count()) > 0 :
            gl = GameLink.objects.get(uid=uid,game=game)
            gl.game = game
            gl.name = name
            gl.sid = sid
            gl.save()
        else:
            GameLink.objects.create(uid=uid,game=game,name=name,sid=sid)

def setStatsValue(j, s):
    try:
        return j['stats'][s]
    except Exception as e:
        return 0
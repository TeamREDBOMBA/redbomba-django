# -*- coding: utf-8 -*-
 
# Create your views here.
import urllib
import random
from redbomba.home.Func import *
from redbomba.home.models import Game
from redbomba.home.models import GameLink
from redbomba.home.models import Notification
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils.timezone import utc
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect

######################################## Views ########################################

def summoner(request):
  try:
    apikey = [
    "fa072bf3-4b01-4719-8036-e3c32c1fd108",
    "382f860d-58b6-420e-b769-049b36c6f862",
    "1cb3ed80-344a-47e3-b03d-1344bde33f30"
    ]
    user = request.POST['user']
    if user != "" :
      random.shuffle(apikey)
      json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v1.4/summoner/by-name/%s?api_key=%s' %(user,apikey[0])))
      summoner_info = json_res[user]
      
      random.shuffle(apikey)
      json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v2.3/league/by-summoner/%s?api_key=%s' %(summoner_info['id'],apikey[0])))
      
      for res in json_res[0]['entries'] :
        if res['playerOrTeamId'] == str(summoner_info['id']) :
          tier = res['tier']
          rank = res['rank']
          lp = res['leaguePoints']
          break

      random.shuffle(apikey)
      json_res = get_json(iriToUri('https://kr.api.pvp.net/api/lol/kr/v1.3/stats/by-summoner/%s/summary?season=SEASON4&api_key=%s' %(summoner_info['id'],apikey[0])))
      for res in json_res['playerStatSummaries'] :
        if res['playerStatSummaryType'] == "RankedSolo5x5" :
          wins = res['wins']
          losses = res['losses']
          break
      summoner_stat = {'tier':tier,'rank':rank,'lp':lp,'wins':wins,'losses':losses}
      
      try:
        summoner_most = []
        cham = BeautifulSoup(urllib.urlopen(iriToUri('http://www.op.gg/summoner/userName=%s' %(user)))).findAll('div', {'class': 'ChampionBox'})
        for i in range(0,3) :
          cham_res={
          "img":cham[i].findAll('img')[0]['src'],
          "name":cham[i].findAll('span', {'class': 'name'})[0].contents[0],
          "kda":cham[i].findAll('span', {'class': 'kda'})[0].contents[0][:-2],
          "played":cham[i].findAll('span', {'class': 'played'})[0].contents[0]
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

      try :
        isLinked = GameLink.objects.get(name=summoner_info['name'])
      except Exception as e:
        isLinked = None

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
  except Exception as e:
    context = {
        'error':'error:'+e.message,
        'from':request.GET['from']
      }
    return render(request, 'search_lol.html', context)
  
def write_GameLink(request):
  if request.method=='POST':
    dfrom = request.POST["from"]
    if request.POST["action"] == "insert" :
      try :
        uid = request.user
        game = Game.objects.get(name=request.POST["gid"])
        name = request.POST["name"]
        insertGameLink(uid, game, name)
        return HttpResponseRedirect(dfrom)
      except Exception as e:
        return HttpResponseRedirect(dfrom)
    else :
      try :
        uid = request.user
        game = GameLink.objects.get(id=request.POST["gl"])
        game.delete()
        return HttpResponseRedirect(dfrom)
      except Exception as e:
        return HttpResponseRedirect(dfrom)
  else :
    return HttpResponseRedirect(dfrom)

def insertGameLink(uid, game, name):
  if (uid==0)|(game==None)|(name==None):
    pass
  else:
    gl = GameLink.objects.filter(uid=uid,game=game)
    if int(gl.count()) > 0 :
      gl = GameLink.objects.get(uid=uid,game=game)
      gl.game = game
      gl.name = name
      gl.save()
    else:
      GameLink.objects.create(uid=uid,game=game,name=name)

def setStatsValue(j, s):
  try:
    return j['stats'][s]
  except Exception as e:
    return 0
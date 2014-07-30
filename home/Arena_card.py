# -*- coding: utf-8 -*-

# Create your views here.
from redbomba.home.Func import *
from redbomba.home.forms import *
from redbomba.home.Arena_matchmaker import *
from redbomba.home.models import Tutorial
from redbomba.home.models import Chatting
from redbomba.home.models import GroupMember
from redbomba.home.models import League
from redbomba.home.models import LeagueTeam
from redbomba.home.models import LeagueRound
from redbomba.home.models import LeagueMatch
from redbomba.home.models import Tutorial
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect

from django import template
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render
from django.db.models import Q, Max, Min
from redbomba.home.models import UserProfile
from redbomba.home.models import Contents
from redbomba.home.models import Group
from redbomba.home.models import GameLink
from redbomba.home.models import LeagueReward

######################################## Views ########################################

def getCard(request):
    league_id = request.POST.get("league_id")
    if league_id :
        return HttpResponse(cardDetail_sorter(request, league_id))
    else :
        return HttpResponse(cardsorter())

def setLeagueteam(request):
    action = request.POST.get("action")
    if action == "insert":
        feasible_time = request.POST["feasible_time"]
        group_id = get_or_none(GroupMember,uid=request.user)
        if group_id :
            group_id = group_id.gid
        round = LeagueRound.objects.get(league_id=League.objects.get(id=request.POST["league_id"]),round=request.POST["round"])
        LeagueTeam.objects.create(
            group_id=group_id,
            round=round,
            feasible_time=feasible_time
        )
        if request.POST.get("round",0) >= 2 :
            lr = LeagueRound.objects.get(league_id=League.objects.get(id=request.POST["league_id"]),round=int(request.POST["round"])-1)
            for lt in LeagueTeam.objects.filter(round=lr) :
                for lm in LeagueMatch.objects.filter((Q(team_a=lt)|Q(team_b=lt))&~Q(state=10)):
                    return HttpResponse("Not Finish")
            lr.is_finish = 1
            lr.save()
    elif action == "delete":
        group_id = GroupMember.objects.get(uid=request.user).gid
        round = LeagueRound.objects.get(league_id=League.objects.get(id=request.POST["league_id"]),round=request.POST["round"])
        LeagueTeam.objects.filter(group_id=group_id,round=round).delete()
    elif action == "abstain":
        try :
            gid = GroupMember.objects.get(uid=request.user).gid
            lr = LeagueRound.objects.get(league_id__id=request.POST["league_id"],round=request.POST["round"])
            lt = LeagueTeam.objects.get(group_id=gid,round=lr)
            lm = LeagueMatch.objects.get(Q(team_a=lt)|Q(team_b=lt))
            lm.state = 10
            if lm.team_a == lt :
                lm.result = 'B'
            elif lm.team_b == lt :
                lm.result = 'A'
            lm.save()
        except Exception as e:
            return HttpResponse("error:"+e.message)
    else :
        return HttpResponse("Error")
    return HttpResponse("Success")

def setMatchmaker(request):
    if request.user :
        round = LeagueRound.objects.get(id=request.GET["round"])
        if request.user == round.league_id.uid :
            return HttpResponse(matchmaker(round))
    return HttpResponse('ERROR')

def getLargeCardBtn(request):
    if request.user :
        try:
            league = League.objects.get(id=request.POST['lid'])
            user = GroupMember.objects.get(uid__id=request.POST['uid'])
        except Exception as e:
            league = None
            user = None
        context = {
            'state':LeagueState(league,user)
        }
        return render(request, 'card_l_btn.html', context)

def setTutorial(request):
    if request.user :
        uid = get_or_none(Tutorial,uid=request.user)
        if uid :
            uid.is_pass1 = 1
            uid.save()
        else :
            Tutorial.objects.create(uid=request.user,is_pass1=1)
    return HttpResponse('ERROR')

def cardsorter():
    query_league = League.objects.all()
    template = get_template('card.html')
    val = ""
    for leagueElem in query_league:
        round = LeagueRound.objects.get(league_id=leagueElem,round=1)
        lt = LeagueTeam.objects.filter(round=round)
        variables = Context({
            'league':leagueElem,
            'host':leagueElem.uid,
            'round':LeagueRound.objects.filter(league_id=leagueElem),
            'SR':LeagueRound.objects.filter(league_id=leagueElem).aggregate(min=Min('start')),
            'ER':LeagueRound.objects.filter(league_id=leagueElem).aggregate(max=Max('end')),
            'reward_1':LeagueReward.objects.get(league_id=leagueElem,name='1'),
            'reward_2':LeagueReward.objects.get(league_id=leagueElem,name='2'),
            'reward_3':LeagueReward.objects.get(league_id=leagueElem,name='3'),
            'poster':Contents.objects.get(uto=leagueElem.id,utotype='l',ctype='img').con,
            'countdown':leagueElem.get_time_diff,
            'isStart': LeagueMatch.objects.filter(Q(team_a__in=lt)|Q(team_b__in=lt)).count(),
            'joined_team':LeagueTeam.objects.filter(round=LeagueRound.objects.get(league_id=leagueElem,round='1')).count()
        })
        output = template.render(variables)
        val = val+output;
    return val

def cardDetail_sorter(request, league_id):
    league = get_or_none(League,id=league_id)
    user = get_or_none(GroupMember,uid=request.user)

    info = get_or_none(Contents,uto=league.id,utotype='l',ctype='inf')
    if info :
        info = info.con
        info = info.replace("# ","",1)
        info = info.split("\n# ")
        con = {
            "txt":get_or_none(Contents,uto=league.id,utotype='l',ctype='txt'),
            "poster":get_or_none(Contents,uto=league.id,utotype='l',ctype='img').con,
            "info":info
        }

    groups = Group.objects.filter(id__in=LeagueTeam.objects.filter(round=get_or_none(LeagueRound,league_id=league,round=1)).values_list('group_id', flat=True))

    try:
        round1 = {"day":range((LeagueRound.objects.get(league_id=league,round=1).end - LeagueRound.objects.get(league_id=league,round=1).start).days+1)}
    except Exception as e:
        round1 = None

    rounds = LeagueRound.objects.filter(league_id=league)

    SR={}
    ER={}

    SR = LeagueRound.objects.filter(league_id=league).aggregate(min=Min('start'))
    SR['league'] = LeagueRound.objects.filter(league_id=league).annotate(Min('start'))[0]
    ER = LeagueRound.objects.filter(league_id=league).aggregate(max=Max('end'))
    ER['league'] = LeagueRound.objects.filter(league_id=league).annotate(Max('end'))[0]

    context = {
        'user': user,
        'league':league,
        'contents':con,
        'groups':groups,
        'round1':round1,
        'rounds':rounds,
        'SR':SR,
        'ER':ER,
        }
    return render(request, 'card_l.html', context)
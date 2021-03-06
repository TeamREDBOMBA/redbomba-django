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
        user = request.POST.get("id")
        if user == None:
            user = request.user
        feasible_time = request.POST["feasible_time"]
        round = int(request.POST.get("round",'1'))
        is_complete = int(request.POST.get('is_complete',1))
        group = get_or_none(GroupMember,user=user)
        if group :
            group = group.group
        lr = LeagueRound.objects.get(league=League.objects.get(id=request.POST.get("league_id")),round=round)
        LeagueTeam.objects.create(
            group=group,
            round=lr,
            feasible_time=feasible_time,
            is_complete = is_complete
        )
        if round >= 2 :
            lr = LeagueRound.objects.get(league=League.objects.get(id=request.POST["league_id"]),round=round-1)
            for lt in LeagueTeam.objects.filter(round=lr,is_complete=1) :
                for lm in LeagueMatch.objects.filter((Q(team_a=lt)|Q(team_b=lt))&~Q(state=10)):
                    return HttpResponse("Not Finish")
            lr.is_finish = 1
            lr.save()
        return HttpResponse("Success")
    elif action == "delete":
        user = request.POST.get("id")
        if user == None:
            user = request.user
        group = GroupMember.objects.get(user=user).group
        round = LeagueRound.objects.get(league_id=League.objects.get(id=request.POST["league_id"]),round=request.POST["round"])
        LeagueTeam.objects.filter(group=group,round=round).delete()
        return HttpResponse("Success")
    elif action == "abstain":
        try :
            user = request.POST.get("id")
            if user == None:
                user = request.user
            group = GroupMember.objects.get(user=user).group
            lr = LeagueRound.objects.get(league__id=request.POST["league_id"],round=request.POST["round"])
            lt = LeagueTeam.objects.get(group=group,round=lr,is_complete=1)
            lm = LeagueMatch.objects.get(Q(team_a=lt)|Q(team_b=lt))
            lm.state = 10
            if lm.team_a == lt :
                lm.result = 'B'
            elif lm.team_b == lt :
                lm.result = 'A'
            lm.save()
            return HttpResponse("Success")
        except Exception as e:
            return HttpResponse("error:"+e.message)
    else :
        return HttpResponse("Error")
    return HttpResponse("Success")

def setMatchmaker(request):
    if request.user :
        round = LeagueRound.objects.get(id=request.GET["round"])
        if request.user == round.league.host :
            return HttpResponse(matchmaker(round))
    return HttpResponse('ERROR')

def getLargeCardBtn(request):
    user = None
    league = get_or_none(League, id=request.POST.get('lid'))
    if request.user.id is not None :
        user = get_or_none(User, id=request.POST.get('uid'))
        if user is None :
            user = request.user
    context = {
        'state':LeagueState(league,user)
    }
    return render(request, 'card_l_btn.html', context)

def setTutorial(request):
    if request.user :
        uid = get_or_none(Tutorial,user=request.user)
        if uid :
            uid.is_pass1 = 1
            uid.save()
        else :
            Tutorial.objects.create(user=request.user,is_pass1=1)
    return HttpResponse('ERROR')

def cardsorter():
    query_league = League.objects.all()
    template = get_template('card_league.html')
    val = ""
    for leagueElem in query_league:
        round = LeagueRound.objects.get(league=leagueElem,round=1)
        lt = LeagueTeam.objects.filter(round=round,is_complete=1)
        variables = Context({
            'league':leagueElem,
            'host':leagueElem.host,
            'round':LeagueRound.objects.filter(league=leagueElem),
            'SR':LeagueRound.objects.filter(league=leagueElem).aggregate(min=Min('start')),
            'ER':LeagueRound.objects.filter(league=leagueElem).aggregate(max=Max('end')),
            'reward_1':LeagueReward.objects.get(league=leagueElem,name='1'),
            'reward_2':LeagueReward.objects.get(league=leagueElem,name='2'),
            'reward_3':LeagueReward.objects.get(league=leagueElem,name='3'),
            'poster':"/media/%s"%(leagueElem.poster),
            'countdown':leagueElem.get_time_diff,
            'isStart': LeagueMatch.objects.filter(Q(team_a__in=lt)|Q(team_b__in=lt)).count(),
            'joined_team':LeagueTeam.objects.filter(round=LeagueRound.objects.get(league=leagueElem,round='1'),is_complete=1).count()
        })
        output = template.render(variables)
        val = val+output;
    return val

def cardDetail_sorter(request=None, league_id=None):
    user = None
    if request.user.id :
        user = get_or_none(GroupMember,user=request.user)

    league = get_or_none(League,id=league_id)

    if user :
        user_group = user.group
        user = user.user
    elif request.user.id :
        user = request.user
        user_group = None
    else :
        user = None
        user_group = None

    rule = league.rule
    if rule :
        rule = rule.replace("# ","",1)
        rule = rule.split("\n# ")
    con = {
        "concept":league.concept,
        "poster":"/media/%s"%(league.poster),
        "rule":rule
    }

    groups = Group.objects.filter(id__in=LeagueTeam.objects.filter(round=get_or_none(LeagueRound,league=league,round=1),is_complete=1).values_list('group', flat=True))

    try:
        round1 = {"day":range((LeagueRound.objects.get(league=league,round=1).end - LeagueRound.objects.get(league=league,round=1).start).days+1)}
    except Exception as e:
        round1 = None

    rounds = LeagueRound.objects.filter(league=league)

    SR={}
    ER={}

    SR = LeagueRound.objects.filter(league=league).aggregate(min=Min('start'))
    SR['league'] = LeagueRound.objects.filter(league=league).annotate(Min('start'))[0]
    ER = LeagueRound.objects.filter(league=league).aggregate(max=Max('end'))
    ER['league'] = LeagueRound.objects.filter(league=league).annotate(Max('end'))[0]

    context = {
        'user': user,
        'user_group': user_group,
        'league':league,
        'contents':con,
        'groups':groups,
        'round1':round1,
        'rounds':rounds,
        'SR':SR,
        'ER':ER,
        'state':LeagueState(league,user)
        }
    return render(request, 'card_l.html', context)
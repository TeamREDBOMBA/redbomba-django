# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from redbomba.arena.models import LeagueRound, LeagueTeam, LeagueMatch
from redbomba.group.models import GroupMember, Group
from redbomba.home.models import get_or_none


def battle(request,round=None):
    round = LeagueRound.objects.get(id=round)
    group = GroupMember.objects.get(user=request.user,is_active=1).group
    lt = LeagueTeam.objects.get(group=group,round=round)
    lm = LeagueMatch.objects.filter(Q(team_a=lt)|Q(team_b=lt)).order_by("-game")[0]
    win_a =  LeagueMatch.objects.filter((Q(team_a=lt)|Q(team_b=lt)),state=10,result="A")
    win_b =  LeagueMatch.objects.filter((Q(team_a=lt)|Q(team_b=lt)),state=10,result="B")

    next_round = get_or_none(LeagueRound,league=round.league,round=(int(round.round)+1))
    next_lt = get_or_none(LeagueTeam,group=group,round=next_round)
    host = get_or_none(User,id=lm.host)

    try:
        nextCount = range((next_round.end-next_round.start).days+1)
    except Exception as e:
        nextCount=None

    try:
        if lm.state == 0:
            group_leader = Group.objects.get(leader=request.user).leader
            if group_leader :
                lm.host = group_leader.id
                lm.state = 1
                lm.result = group_leader.id
                lm.save()
    except Exception as e:
        pass

    try:
        bo = round.bestof
        if bo > 1 :
            game_str = "%d전%d선승" %(bo,bo-bo/2)
        else :
            game_str = "단판게임"
    except Exception as e:
        game_str = "단판게임"

    context = {
        'user': request.user,
        'group' : group,
        'league': lm,
        'host':host,
        'next_round':next_round,
        'next_lt':next_lt,
        'nextCount':nextCount,
        'win_a': win_a,
        'win_b': win_b,
        'bo':game_str,
        'from' : '/battle/'
    }
    return render(request, 'battle.html', context)
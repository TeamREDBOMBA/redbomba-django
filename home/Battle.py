# -*- coding: utf-8 -*-

# Create your views here.
from redbomba.home.Func import *
from redbomba.home.models import Group
from redbomba.home.models import GroupMember
from redbomba.home.models import LeagueTeam
from redbomba.home.models import LeagueRound
from redbomba.home.models import LeagueMatch
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render

######################################## Views ########################################

def battle(request):
    round = LeagueRound.objects.get(id=request.GET.get('round'))
    group = GroupMember.objects.get(user=request.user,is_active=1).group
    lt = LeagueTeam.objects.get(group=group,round=round)
    lm = LeagueMatch.objects.filter(Q(team_a=lt)|Q(team_b=lt)).order_by("-game")[0]
    win_a =  LeagueMatch.objects.filter((Q(team_a=lt)|Q(team_b=lt)),state=10,result="A")
    win_b =  LeagueMatch.objects.filter((Q(team_a=lt)|Q(team_b=lt)),state=10,result="B")

    next_round = get_or_none(LeagueRound,league=round.league,round=(int(round.round)+1))
    next_lt = get_or_none(LeagueTeam,group=group,round=next_round)

    try:
        nextCount = range((next_round.end-next_round.start).days+1)
    except Exception as e:
        nextCount=None

    try:
        if lm.state == 0:
            group_leader = Group.objects.get(leader=request.user).leader
            if group_leader :
                lm.host = group_leader
                lm.state = 1
                lm.result = group_leader.id
                lm.save()
        else :
            lm.host = User.objects.get(id=lm.leader)
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
        'uinfo' : request.user.get_profile,
        'group' : group,
        'league': lm,
        'next_round':next_round,
        'next_lt':next_lt,
        'nextCount':nextCount,
        'win_a': win_a,
        'win_b': win_b,
        'bo':game_str,
        'from' : '/battle/'
    }
    return render(request, 'battle.html', context)
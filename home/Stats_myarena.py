# -*- coding: utf-8 -*-
 
# Create your views here.
from redbomba.home.Func import *
from redbomba.home.models import User
from redbomba.home.models import GroupMember
from redbomba.home.models import GameLink
from redbomba.home.models import League
from redbomba.home.models import LeagueTeam
from django.db.models import Q
from django.shortcuts import render

######################################## Views ########################################

def getMyarena(request):
  if request.user :
    try:
      if request.POST['username'] == request.user.username :
        user = GroupMember.objects.get(uid=request.user)
      else :
        user = GroupMember.objects.get(uid=User.objects.get(username=request.POST['username']))
      league = League.objects.filter(id__in=LeagueTeam.objects.filter(group_id=user.gid).values_list('round__league_id', flat=True))
    except Exception as e:
      user = None
      league = None

    state = []
    try:
      for l in league :
        state.append(LeagueState(l,user))
    except Exception as e:
      state = None

    context = {
      "user":request.user,
      "target_user":user,
      "state":state
      }
    return render(request, 'myarena.html', context)
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
  if request.POST.get('username') :
    user = get_or_none(User,username=request.POST['username'])
  else :
    user = request.user
  user_group = get_or_none(GroupMember,uid=user)
  if user_group :
    league = League.objects.filter(id__in=LeagueTeam.objects.filter(group_id=user_group.gid).values_list('round__league_id', flat=True))
  else:
    league = []

  state = []
  for l in league :
    state.append(LeagueState(l,user))

  context = {
    "user":request.user,
    "target_user":user,
    "state":state
    }
  return render(request, 'myarena.html', context)
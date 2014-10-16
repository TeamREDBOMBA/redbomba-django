# -*- coding: utf-8 -*-
 
# Create your views here.
import random
from django.shortcuts import render
from redbomba.home.models import LeagueMatch
from redbomba.home.models import GlobalCard
from django.db.models import Q
from redbomba.home.Func import *

######################################## Views ########################################

def getLeagueListForDisplay(request):
    query_no = int(request.POST.get("query_no",0))
    leagues = LeagueMatch.objects.filter(~Q(state=10)&~Q(state=0))
    if leagues.count() == 0 :
        return render(request, 'main_display.html', {"count":0})
    bestof = range(leagues[query_no%len(leagues)].team_a.round.bestof)
    context = {'user':request.user,'league':leagues[query_no%len(leagues)],'bestof':bestof}
    return render(request, 'main_display.html', context)


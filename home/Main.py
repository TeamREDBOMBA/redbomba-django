# -*- coding: utf-8 -*-
 
# Create your views here.
import random
from django.shortcuts import render
from redbomba.home.models import LeagueMatch
from django.db.models import Q
from redbomba.home.Func import *

######################################## Views ########################################

def getLeagueListForDisplay(request):
    query_no = int(request.POST.get("query_no",0))
    leagues = LeagueMatch.objects.filter(~Q(state=10)&~Q(state=0))
    context = {'user':request.user,'league':leagues[query_no%len(leagues)]}
    return render(request, 'main_display.html', context)

def getGlobarFeed(request):
    news = []
    user = get_or_none(User,username='gugg')
    for i in range(0,12):
        img = {"src":"http://re01-xv2938.ktics.co.kr/stat_lol_%d.jpg" %(random.randrange(1,620)),"focusx":0.7,"focusy":0.4}
        news.append({"img":img,"title":"제목이 들어갑니다.","txt":"내용이 들어갑니다. 몇 줄이 들어갈까요?","user":user})
    context = {'user':request.user,'news':news}
    return render(request, 'feed_news.html', context)
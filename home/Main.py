# -*- coding: utf-8 -*-
 
# Create your views here.
import random
from django.shortcuts import render
from redbomba.home.models import *
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

def getCardNews(request):
    news = []
    globalfeed = GlobalCard.objects.filter().order_by("-date_updated")
    if globalfeed :
        for gf in globalfeed :
            news.append({"id":gf.id,"title":gf.title,"txt":gf.con,"img":{"src":"/media/%s"%(gf.src),"focusx":gf.focus_x,"focusy":gf.focus_y},"user":gf.user})
        context = {'user':request.user,'news':news}
        return render(request, 'card_news.html', context)
    return HttpResponse("")

def getCardNewsLarge(request, fid=None):
    if fid :
        globalfeed = get_or_none(GlobalCard,id=fid)
        context = {
            'user':request.user,
            'news':globalfeed
        }
        return render(request, 'card_news_large.html', context)
    return HttpResponse(None)

def getCardPrivate(request):
    user = request.user
    news = []

    mygroup = GroupMember.objects.filter(user=user).values_list('group', flat=True)
    if mygroup :
        gm = GroupMember.objects.filter(Q(group__in=mygroup)&~Q(user=user))
        if gm :
            for value in gm :
                news.append({'self':value,'type':'groupmember','date':value.date_updated})

    feed = Feed.objects.filter(ufrom=user.id,ufromtype='u')
    reply = FeedReply.objects.filter(Q(feed__in=feed)&~Q(user=user)).order_by("-date_updated")
    if reply :
        for value in reply :
            news.append({'self':value,'type':'reply','date':value.date_updated})

    pc = PrivateCard.objects.filter(user=user).order_by("-date_updated")
    if pc :
        for value in pc :
            news.append({'self':value,'type':'system','date':value.date_updated})

    news.sort(key=lambda item:item['date'], reverse=True)
    context = {'user':user,'news':news}
    return render(request, 'card_private.html', context)
# -*- coding: utf-8 -*-
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from redbomba.arena.models import LeagueMatch
from redbomba.feed.models import Feed, FeedReply
from redbomba.group.models import GroupMember
from redbomba.home.models import get_or_none, GameLink
from redbomba.main.models import GlobalCard, PrivateCard


def main(request):
    try:
        if request.user.get_profile().is_pass_gamelink == 0 :
            return HttpResponseRedirect("/head/start/")
        gamelink = GameLink.objects.filter(user=request.user)
        context = {
            'gamelink':gamelink,
            'user': request.user,
            'from':'/',
            'appname':'main'
            }
    except Exception as e:
        context = {'user': request.user}
    return render(request, 'main.html', context)

def card_global(request):
    news = []
    globalcards = GlobalCard.objects.filter().order_by("-date_updated")
    if globalcards :
        for gf in globalcards :
            news.append({"id":gf.id,"title":gf.title,"txt":gf.con,"img":{"src":"%s"%(gf.src.url),"focusx":gf.focus_x,"focusy":gf.focus_y},"user":gf.user})
        context = {'user':request.user,'news':news}
        return render(request, 'card_global.html', context)
    return HttpResponse("")

def card_global_large(request, fid=None):
    if fid :
        gf = get_or_none(GlobalCard,id=fid)
        context = {
            'user':request.user,
            'news':gf
        }
        return render(request, 'card_global_large.html', context)
    return HttpResponse(None)

def card_private(request):
    user = request.user
    group = user.get_profile().get_group()
    news = []

    mygroup = GroupMember.objects.filter(user=user).values_list('group', flat=True)
    if mygroup :
        gm = GroupMember.objects.filter(Q(group__in=mygroup)&~Q(user=user))
        if gm :
            for value in gm :
                news.append({'self':value,'type':'groupmember','date':value.date_updated})

    feeds = Feed.objects.filter(user=user)
    for feed in feeds :
        reply = feed.reply.filter(~Q(user=user)).order_by("-date_updated")
        if reply :
            for value in reply :
                news.append({'self':value,'type':'reply','date':value.date_updated})

    pc = PrivateCard.objects.filter(user=user).order_by("-date_updated")
    if pc :
        for value in pc :
            news.append({'self':value,'type':'system','date':value.date_updated})

    lm = LeagueMatch.objects.filter(Q(team_a__group__in=group)|Q(team_b__group__in=group)&Q(state=10)).order_by("-date_updated")
    if lm :
        for value in lm :
            news.append({'self':value,'type':'leaguematch','date':value.date_updated})

    news.sort(key=lambda item:item['date'], reverse=True)
    context = {'user':user,'news':news}
    return render(request, 'card_private.html', context)
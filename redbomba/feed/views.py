# -*- coding: utf-8 -*-

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from redbomba.arena.models import League
from redbomba.feed.models import Feed, FeedContents, FeedReply
from redbomba.home.models import get_or_none
from redbomba.main.models import GlobalCard

def feed(request):
    gcid = request.GET.get("gcid")
    lid = request.GET.get("lid")
    len = request.GET.get("len")

    feeds = []
    if gcid :
        gc = get_or_none(GlobalCard,id=gcid)
        if gc :
            for feed in gc.feeds.all().order_by("-id")[:len] :
                feeds.append(feed)
    elif lid :
        league = get_or_none(League,id=lid)
        if league :
            for feed in league.feeds.all().order_by("-id")[:len] :
                feeds.append(feed)
    context = {'user':request.user,'feeds':feeds}
    return render(request, 'feed.html', context)

def feed_post(request):
    gcid = request.GET.get("gcid")
    lid = request.GET.get("lid")
    con_txt = request.POST.get("con_txt")
    con_img = request.POST.get("con_img")

    if gcid :
        fid = Feed.objects.create(user=request.user)
        if con_txt : fid.con.add(FeedContents.objects.create(type='txt',con=con_txt))
        if con_img : fid.con.add(FeedContents.objects.create(type='img',con=con_img))
        gc = get_or_none(GlobalCard,id=gcid)
        gc.feeds.add(fid)

        return feed(request)
    elif lid :
        fid = Feed.objects.create(user=request.user)
        if con_txt : fid.con.add(FeedContents.objects.create(type='txt',con=con_txt))
        if con_img : fid.con.add(FeedContents.objects.create(type='img',con=con_img))
        league = get_or_none(League,id=lid)
        league.feeds.add(fid)

        return feed(request)
    return HttpResponse("입력 실패")

def feed_reply(request):
    fid = request.GET.get("fid")
    len = request.GET.get("len")

    replies = []
    feed_ele = get_or_none(Feed,id=fid)
    if feed_ele :
        for reply in feed_ele.reply.all().order_by("-id")[:len] :
            replies.append(reply)
    context = {'user':request.user,'feed':feed_ele,'replies':replies}
    return render(request, 'feed_reply.html', context)

def feed_reply_post(request):
    fid = request.GET.get("fid")
    con = request.POST.get("con")

    feed_ele = get_or_none(Feed,id=fid)
    if feed_ele :
        if con : feed_ele.reply.add(FeedReply.objects.create(user=request.user,con=con))
        return feed_reply(request)
    return HttpResponse("입력 실패")
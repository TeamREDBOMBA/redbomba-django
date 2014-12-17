# -*- coding: utf-8 -*-

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from redbomba.feed.models import Feed, FeedContents
from redbomba.home.models import get_or_none
from redbomba.main.models import GlobalCard

def feed(request):
    gcid = request.GET.get("gcid")
    len = request.GET.get("len")

    feeds = []
    if gcid :
        gc = get_or_none(GlobalCard,id=gcid)
        if gc :
            for feed in gc.feeds.all().order_by("-id")[:len] :
                feeds.append(feed)
    context = {'user':request.user,'feeds':feeds}
    return render(request, 'feed_body.html', context)

def feed_post(request):
    gcid = request.GET.get("gcid")
    con_txt = request.POST.get("con_txt")
    con_img = request.POST.get("con_img")

    if gcid :
        fid = Feed.objects.create(user=request.user)
        if con_txt : fid.con.add(FeedContents.objects.create(type='txt',con=con_txt))
        if con_img : fid.con.add(FeedContents.objects.create(type='img',con=con_img))
        gc = get_or_none(GlobalCard,id=gcid)
        gc.feeds.add(fid)

        return feed(request)
    return HttpResponse("입력 실패")
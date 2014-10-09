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
    if leagues.count() == 0 :
        return render(request, 'main_display.html', {"count":0})
    context = {'user':request.user,'league':leagues[query_no%len(leagues)]}
    return render(request, 'main_display.html', context)

def getGlobarFeed(request):
    news = []
    user = get_or_none(User,username='gugg')
    news.append({"title":"[이벤트] 고수 초대석, 이번주 게스트를 알아맞춰 보세요","txt":"12월 13일, 고수 초대석에 모셔질 게스트를 맞추시는 분들에게 푸짐한 상품을...","img":{"src":"/media/tmp/1.jpg","focusx":0.0,"focusy":0.0},"user":user})
    news.append({"title":"홍진호, 위제네레이션","txt":"프로게이머 출신 방송인 홍진호가 위제네레이션과 손잡고 기부 문화의 새장을...","img":{"src":"/media/tmp/2.jpg","focusx":0.0,"focusy":0.15},"user":user})
    news.append({"title":"프로게이머의 인성 문제, 이대로 괜찮은가","txt":"최근 IEM Season6에서의 일이다. Moscow5의 정글러 Diamondprox가...","img":{"src":"/media/tmp/3.jpg","focusx":0.7,"focusy":0.5},"user":user})
    news.append({"title":"나진 e-empire, 오늘 창단식 열려","txt":"나진 e-Empire가 오늘 나진 상가홀에서 성대한 창단식을 열고 공식적인...","img":{"src":"/media/tmp/4.jpg","focusx":0.0,"focusy":0.0},"user":user})
    news.append({"title":"[포토] 부스에서 롤 중인 강존야 해설","txt":None,"img":{"src":"/media/tmp/5.jpg","focusx":0.0,"focusy":0.0},"user":user})
    news.append({"title":"게임 대회도 하고, 기부도 하자","txt":'"Play for help", 게임 대회에 우승하면 우승자의 이름으로 기부를...',"img":{"src":"/media/tmp/6.jpg","focusx":-0.3,"focusy":0.0},"user":user})
    news.append({"title":"[칼럼] 롤드컵, 이제는 바뀌어야 할 때","txt":"리그 오브 레전드 월드 챔피언쉽(이하 '롤드컵')이 마무리에 들어갔다. 하지만...","img":{"src":"/media/tmp/7.jpg","focusx":0.0,"focusy":-0.2},"user":user})
    context = {'user':request.user,'news':news}
    return render(request, 'feed_news.html', context)
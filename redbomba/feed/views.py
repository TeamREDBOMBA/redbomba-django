from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from redbomba.home.models import get_or_none
from redbomba.main.models import GlobalCard


def feed_card_global(request):
    news = []
    globalcards = GlobalCard.objects.filter().order_by("-date_updated")
    if globalcards :
        for gf in globalcards :
            news.append({"id":gf.id,"title":gf.title,"txt":gf.con,"img":{"src":"%s"%(gf.src.url),"focusx":gf.focus_x,"focusy":gf.focus_y},"user":gf.user})
        context = {'user':request.user,'news':news}
        return render(request, 'feed_card_global.html', context)
    return HttpResponse("")

def feed_card_global_large(request, fid=None):
    if fid :
        gf = get_or_none(GlobalCard,id=fid)
        context = {
            'user':request.user,
            'news':gf
        }
        return render(request, 'feed_card_global_large.html', context)
    return HttpResponse(None)
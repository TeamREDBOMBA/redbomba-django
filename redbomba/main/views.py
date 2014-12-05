from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from redbomba.main.models import GlobalCard


def main(request):
    try:
        context = {
            'user': request.user,
            'from':'/',
            'appname':'main'
            }
    except Exception as e:
        context = {'user': request.user}
    return render(request, 'main.html', context)

def main_globalcard(request):
    news = []
    globalcards = GlobalCard.objects.filter().order_by("-date_updated")
    if globalcards :
        for gf in globalcards :
            news.append({"id":gf.id,"title":gf.title,"txt":gf.con,"img":{"src":"/%s"%(gf.src),"focusx":gf.focus_x,"focusy":gf.focus_y},"user":gf.user})
        context = {'user':request.user,'news':news}
        return render(request, 'main_globalcard.html', context)
    return HttpResponse("")
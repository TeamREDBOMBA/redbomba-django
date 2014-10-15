# -*- coding: utf-8 -*-

# Create your views here.
from redbomba.home.Func import *
from redbomba.home.models import Contents
from redbomba.home.models import Reply
from redbomba.home.models import GlobalFeed
from redbomba.home.models import Feed
from redbomba.home.models import Smile
from redbomba.home.models import League
from redbomba.home.models import Check
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.shortcuts import render

######################################## Views ########################################

def read_Feed_pri(request) :
    uid = get_or_none(User,username=request.GET.get("username"))
    if uid : uid = int(uid.id)
    else : uid = request.user.id
    len = int(request.GET.get("len",0))
    fid = int(request.GET.get("fid",0))
    return HttpResponse(feedsorter("private", uid, len, fid, request))

def read_Feed_pub(request) :
    len = int(request.GET.get("len",0))
    fid = int(request.GET.get("fid",0))
    return HttpResponse(feedsorter("public", request.user.id, len, fid, request))

def read_Feed_card(request) :
    len = int(request.GET.get("len",0))
    fid = int(request.GET.get("fid",0))
    lid = int(request.GET.get("league_id",0))
    return HttpResponse(feedsorter("card", lid, len, fid, request))

def read_Feed_news_detail(request, fid=None):
    len = int(request.GET.get("len",0))
    fid = int(request.GET.get("fid",0))
    gfid = int(request.GET.get("gfid",0))
    return HttpResponse(feedsorter("globalfeed", gfid, len, fid, request))

def read_Feed_news(request):
    news = []
    globalfeed = GlobalFeed.objects.filter().order_by("-date_updated")
    for gf in globalfeed :
        news.append({"id":gf.id,"title":gf.title,"txt":gf.con,"img":{"src":"/media/%s"%(gf.src),"focusx":gf.focus_x,"focusy":gf.focus_y},"user":gf.uid})
    context = {'user':request.user,'news':news}
    return render(request, 'card_news.html', context)

def read_Feed_news_page(request, fid=None):
    if fid :
        globalfeed = get_or_none(GlobalFeed,id=fid)
        context = {
            'user':request.user,
            'news':globalfeed
        }
        return render(request, 'card_news_large.html', context)
    return HttpResponse(None)

def setSmile(request):
    if request.user :
        fid = request.GET.get("fid")
        action = request.GET.get("action")
        loc = request.GET.get("loc")
        uid = request.user.id
        if (fid or action or loc) == 0 : return HttpResponse("error")
        if action == "insert" : insertSmile(fid, uid)
        else : deleteSmile(fid, uid)
        if loc == "pri" : return HttpResponse(feedsorter("private", request.user.id, 1, fid, request))
        elif loc == "pub" : return HttpResponse(feedsorter("public", request.user.id, 1, fid, request))
        else : return HttpResponse("error")
    else : return HttpResponse("error")


def write_Feed(request):
    action = request.POST.get("action")
    uid = request.user.id
    utotype = request.POST.get("utotype")
    if utotype == 'u' :
        uto = get_or_none(User,username=request.POST.get("uto"))
    elif utotype == 'l':
        uto = get_or_none(League,id=int(request.POST.get("uto")))
    elif utotype == 'g':
        uto = get_or_none(GlobalFeed,id=int(request.POST.get("uto")))
    if uto :
        uto = uto.id
    feedtype = 1
    txt = request.POST.get("txt")
    tag = request.POST.get("tag")
    img = request.POST.get("img")
    vid = request.POST.get("vid")
    log = request.POST.get("log")
    hyp = request.POST.get("hyp")
    if action == "insert" :
        insertFeed(uid, uto, utotype, feedtype, tag, img, txt, vid, log, hyp)
    else :
        pass
        #deleteFeed(fid, uid)
    loc = request.POST.get("loc","private")
    return HttpResponse(feedsorter(loc, uto, 10, 0, request))

def read_Reply(request) :
    len = int(request.GET.get("len",0))
    fid = int(request.GET.get("fid",0))
    return HttpResponse(replysorter(request.user.id, len, fid))

def write_Reply(request):
    action = request.POST.get("action")
    uid = request.user.id
    fid = request.POST.get("fid")
    txt = request.POST.get("txt")
    if action == "insert" :
        insertReply(uid, fid, txt)
    else :
        pass
        #deleteFeed(fid, uid)
    return HttpResponse(replysorter(uid, 3, fid))

def feedsorter(loc, uid, len, fid, request):
    if loc == "private" :
        user = get_or_none(User,id=uid)
        reply = Reply.objects.filter(ufrom=user).values_list('fid', flat=True)
        smile = Smile.objects.filter(uid=user).values_list('fid', flat=True)
        if fid==0 :
            feed = list(Feed.objects.filter((Q(ufrom=uid)&Q(ufromtype="u"))|(Q(uto=uid)&Q(utotype="u"))|Q(id__in=reply)|Q(id__in=smile)).order_by("-date_updated"))
        else :
            feed = list(Feed.objects.filter(id=fid).order_by("-date_updated"))
        template = get_template('feed_pri.html')
        val = ""
        i=0
        for feedElem in feed:
            if feedElem.utotype == 'u' :
                uto = User.objects.get(id=feedElem.uto).username
            elif feedElem.utotype == 'l' :
                uto = League.objects.get(id=feedElem.uto).name
            variables = Context({
                'ele':fid,
                'fid' : feedElem.id,
                'uid' : uid,
                'ufrom': User.objects.get(id=feedElem.ufrom).username,
                'uto': uto,
                'ufromicon':User.objects.get(id=feedElem.ufrom).get_profile().user_icon,
                'date_updated':feedElem.get_time_diff(),
                'con_txt':Contents.objects.get(uto=feedElem.id, utotype='f', ctype='txt').con,
                'smile':list(Smile.objects.filter(fid=feedElem)),
                'isDone_smile':list(Smile.objects.filter(fid=feedElem,uid=user)),
                'reply_len':Reply.objects.filter(ufrom=user,fid=feedElem)
            })
            Check.objects.get_or_create(fid=feedElem,uid=user)
            if i==len: break
            output = template.render(variables)
            val = val+output;
            i=i+1;
        return val

    elif loc == "public" :
        user = get_or_none(User,id=uid)
        reply = Reply.objects.filter(ufrom=uid).values_list('fid', flat=True)
        smile = Smile.objects.filter(uid=user).values_list('fid', flat=True)
        if fid==0 :
            feed = list(Feed.objects.filter().order_by("-date_updated"))
        else :
            feed = list(Feed.objects.filter(id=fid).order_by("-date_updated"))
        template = get_template('feed_pub.html')
        val = ""
        i=0
        for feedElem in feed:
            if fid==0 :
                c = Check.objects.filter(fid=feedElem).count()
                s = Smile.objects.filter(fid=feedElem).count()
            else :
                c, s = 1, 1
            try:
                if s/c >= 0.5 :
                    variables = Context({
                        'ele':fid,
                        'fid' : feedElem.id,
                        'uid' : uid,
                        'ufrom': User.objects.get(id=feedElem.ufrom).username,
                        'uto': User.objects.get(id=feedElem.uto).username,
                        'ufromicon':User.objects.get(id=feedElem.ufrom).get_profile().user_icon,
                        'date_updated':feedElem.get_time_diff(),
                        'con_txt':Contents.objects.get(uto=feedElem.id,utotype='f', ctype='txt').con,
                        'smile':list(Smile.objects.filter(fid=feedElem)),
                        'isDone_smile':list(Smile.objects.filter(fid=feedElem,uid=user)),
                        'reply_len':Reply.objects.filter(ufrom=uid,fid=feedElem)
                    })
                    if i==len: break
                    output = template.render(variables)
                    val = val+output;
                    i=i+1;
            except Exception as e:
                pass
        return val
    elif loc == "card" :
        if request.user.id :
            user = request.user
        else :
            user = None
        lid = get_or_none(League,id=uid)
        if fid==0 :
            feed = Feed.objects.filter((Q(ufrom=lid.id)&Q(ufromtype="l"))|(Q(uto=lid.id)&Q(utotype="l"))).order_by("-date_updated")
        else :
            feed = Feed.objects.filter(id=fid).order_by("-date_updated")
        template = get_template('feed_body.html')
        val = ""
        i=0
        for feedElem in feed:
            variables = Context({
                'ele':fid,
                'fid' : feedElem.id,
                'uid' : uid,
                'user' : user,
                'ufrom': User.objects.get(id=feedElem.ufrom).username,
                'uto': League.objects.get(id=feedElem.uto).name,
                'ufromicon':User.objects.get(id=feedElem.ufrom).get_profile().user_icon,
                'date_updated':feedElem.get_time_diff(),
                'con_txt':Contents.objects.get(uto=feedElem.id, utotype='f', ctype='txt').con,
                'smile':Smile.objects.filter(fid=feedElem),
                'isDone_smile':get_or_none(Smile,fid=feedElem,uid=user),
                'reply_len':Reply.objects.filter(ufrom=uid,fid=feedElem)
            })
            if i==len: break
            output = template.render(variables)
            val = val+output;
            i=i+1;
        if feed.count() > i :
            btnMore = "<div class='div_feedcard_morebtn' onclick='clickMore()'> more </div>"
        else :
            btnMore=""
        return val+btnMore
    elif loc == "globalfeed" :
        if request.user.id :
            user = request.user
        else :
            user = None
        gfid = get_or_none(GlobalFeed,id=uid)
        if fid==0 :
            feed = Feed.objects.filter((Q(ufrom=gfid.id)&Q(ufromtype="g"))|(Q(uto=gfid.id)&Q(utotype="g"))).order_by("-date_updated")
        else :
            feed = Feed.objects.filter(id=fid).order_by("-date_updated")
        template = get_template('feed_body.html')
        val = ""
        i=0
        for feedElem in feed:
            variables = Context({
                'ele':fid,
                'fid' : feedElem.id,
                'uid' : uid,
                'user' : user,
                'ufrom': User.objects.get(id=feedElem.ufrom).username,
                'uto': GlobalFeed.objects.get(id=feedElem.uto).title,
                'ufromicon':User.objects.get(id=feedElem.ufrom).get_profile().user_icon,
                'date_updated':feedElem.get_time_diff(),
                'con_txt':Contents.objects.get(uto=feedElem.id, utotype='f', ctype='txt').con,
                'smile':Smile.objects.filter(fid=feedElem),
                'isDone_smile':get_or_none(Smile,fid=feedElem,uid=user),
                'reply_len':Reply.objects.filter(ufrom=uid,fid=feedElem)
            })
            if i==len: break
            output = template.render(variables)
            val = val+output;
            i=i+1;
        if feed.count() > i :
            btnMore = "<div class='div_feedcard_morebtn' onclick='clickMore()'> more </div>"
        else :
            btnMore=""
        return val+btnMore
    else :
        return "Loc Error"


def replysorter(uid,len,fid):
    reply = Reply.objects.filter(fid=Feed.objects.get(id=fid)).order_by("-date_updated")
    template = get_template('reply_body.html')
    val = ""
    i=0
    for replyElem in reply:
        variables = Context({
            'fid' : fid,
            'rid' : replyElem.id,
            'ufrom': replyElem.ufrom.username,
            'ufromicon':replyElem.ufrom.get_profile().user_icon,
            'date_updated':replyElem.get_time_diff(),
            'con_txt':Contents.objects.get(uto=replyElem.id, utotype='r', ctype='txt').con
        })
        if i==len: break
        output = template.render(variables)
        val = output+val;
        i=i+1;
    if reply.count() > i :
        btnMore = "<div class='div_feedpri_morebtn' onclick='clickMore_%s_%s()'> more </div>" %(loc,fid)
    else :
        btnMore=""
    return btnMore+val


def insertFeed(uid, uto, utotype, feedtype, tag=None, img=None, txt=None, vid=None, log=None, hyp=None):
    if uid and uto and utotype and txt:
        feed = Feed.objects.create(ufrom=uid,ufromtype="u",uto=uto,utotype=utotype,feedtype=feedtype)
        Contents.objects.create(uto=feed.id,utotype='f',ctype="txt",con=txt)
        if tag : Contents.objects.create(uto=feed.id,utotype='f',ctype="tag",con=tag)
        if img : Contents.objects.create(uto=feed.id,utotype='f',ctype="img",con=img)
        if vid : Contents.objects.create(uto=feed.id,utotype='f',ctype="vid",con=vid)
        if log : Contents.objects.create(uto=feed.id,utotype='f',ctype="log",con=log)
        if hyp : Contents.objects.create(uto=feed.id,utotype='f',ctype="hyp",con=hyp)
    else:
        pass

def insertSmile(fid, uid):
    if (fid==None)|(uid==None):
        pass
    else:
        Smile.objects.create(fid=Feed.objects.get(id=fid),uid=User.objects.get(id=uid))

def deleteSmile(fid=None, uid=None):
    if fid and uid:
        Smile.objects.filter(fid=Feed.objects.get(id=fid),uid=User.objects.get(id=uid)).delete()

def insertReply(uid, fid, txt):
    if uid and fid and txt:
        reply = Reply.objects.create(ufrom=User.objects.get(id=uid),fid=Feed.objects.get(id=fid))
        Contents.objects.create(uto=reply.id,utotype='r',ctype="txt",con=txt)
# -*- coding: utf-8 -*-

# Create your views here.
from redbomba.home.Func import *
from redbomba.home.models import FeedContents, get_or_none
from redbomba.home.models import FeedReply
from redbomba.home.models import GlobalCard
from redbomba.home.models import Feed
from redbomba.home.models import FeedSmile
from redbomba.home.models import League
from redbomba.home.models import FeedCheck
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

def read_Feed_card(request) :
    len = int(request.GET.get("len",0))
    fid = int(request.GET.get("fid",0))
    lid = request.GET.get("league_id",0)
    return HttpResponse(feedsorter("card", lid, len, fid, request))

def read_Feed_news_detail(request, fid=None):
    len = int(request.GET.get("len",0))
    fid = int(request.GET.get("fid",0))
    gfid = int(request.GET.get("gfid",0))
    return HttpResponse(feedsorter("globalfeed", gfid, len, fid, request))

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
    uto = None
    if utotype == 'u' :
        uto = get_or_none(User,username=request.POST.get("uto"))
    elif utotype == 'l':
        uto = get_or_none(League,id=int(request.POST.get("uto")))
    elif utotype == 'g':
        uto = get_or_none(GlobalCard,id=int(request.POST.get("uto")))
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
        reply = FeedReply.objects.filter(user=user).values_list('feed', flat=True)
        smile = FeedSmile.objects.filter(user=user).values_list('feed', flat=True)
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
                'con_txt':FeedContents.objects.get(uto=feedElem.id, utotype='f', ctype='txt').con,
                'smile':list(FeedSmile.objects.filter(feed=feedElem)),
                'isDone_smile':list(FeedSmile.objects.filter(feed=feedElem,user=user)),
                'reply_len':FeedReply.objects.filter(user=user,feed=feedElem)
            })
            FeedCheck.objects.get_or_create(feed=feedElem,user=user)
            if i==len: break
            output = template.render(variables)
            val = val+output;
            i=i+1;
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
            id = feedElem.id
            variables = Context({
                'ele':fid,
                'fid' : feedElem.id,
                'uid' : uid,
                'user' : user,
                'ufrom': get_or_none(User,id=feedElem.ufrom),
                'uto': League.objects.get(id=feedElem.uto).name,
                'date_updated':feedElem.get_time_diff(),
                'con_txt':feedElem.get_con('txt').con,
                'smile':FeedSmile.objects.filter(feed=feedElem),
                'isDone_smile':get_or_none(FeedSmile,feed=feedElem,user=user),
                'reply_len':FeedReply.objects.filter(user=uid,feed=feedElem)
            })
            if i==len: break
            output = template.render(variables)
            val = val+output;
            i=i+1;
        if feed.count() > i :
            btnMore = """<div class='div_feedcard_morebtn' onclick='clickMore(feed_league_len,"#div_right_feed","/feed/card/?league_id=%d")'> more </div>"""%(lid.id)
        else :
            btnMore=""
        return val+btnMore
    elif loc == "globalfeed" :
        if request.user.id :
            user = request.user
        else :
            user = None
        gfid = get_or_none(GlobalCard,id=uid)
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
                'ufrom': get_or_none(User,id=feedElem.ufrom),
                'uto': GlobalCard.objects.get(id=feedElem.uto).title,
                'date_updated':feedElem.get_time_diff(),
                'con_txt':feedElem.get_con('txt').con,
                'smile':FeedSmile.objects.filter(feed=feedElem),
                'isDone_smile':get_or_none(FeedSmile,feed=feedElem,user=user),
                'reply_len':FeedReply.objects.filter(user=uid,feed=feedElem)
            })
            if i==len: break
            output = template.render(variables)
            val = val+output;
            i=i+1;
        if feed.count() > i :
            btnMore = """<div class='div_feedcard_morebtn' onclick='clickMore(feed_news_len,"#div_right_feed","/feed/news/detail/?gfid=%d")'> more </div>"""%(gfid.id)
        else :
            btnMore=""
        return val+btnMore
    else :
        return "Loc Error"


def replysorter(uid,len,fid):
    reply = FeedReply.objects.filter(feed=Feed.objects.get(id=fid)).order_by("-date_updated")
    template = get_template('reply_body.html')
    val = ""
    i=0
    for replyElem in reply:
        variables = Context({
            'fid' : fid,
            'rid' : replyElem.id,
            'user': replyElem.user,
            'date_updated':replyElem.get_time_diff(),
            'con_txt':replyElem.con
        })
        if i==len: break
        output = template.render(variables)
        val = output+val;
        i=i+1;
    if reply.count() > i :
        btnMore = "<div class='div_feedpri_morebtn' onclick='clickMore_%s()'> more </div>" %(fid)
    else :
        btnMore=""
    return btnMore+val


def insertFeed(uid, uto, utotype, feedtype, tag=None, img=None, txt=None, vid=None, log=None, hyp=None):
    if uid and uto and utotype and txt:
        feed = Feed.objects.create(ufrom=uid,ufromtype="u",uto=uto,utotype=utotype,feedtype=feedtype)
        FeedContents.objects.create(feed=feed,contype="txt",con=txt)
        if tag and tag != 0 and tag!= "0" : FeedContents.objects.create(feed=feed,contype="tag",con=tag)
        if img and img != 0 and img!= "0" : FeedContents.objects.create(feed=feed,contype="img",con=img)
        if vid and vid != 0 and vid!= "0" : FeedContents.objects.create(feed=feed,contype="vid",con=vid)
        if log and log != 0 and log!= "0" : FeedContents.objects.create(feed=feed,contype="log",con=log)
        if hyp and hyp != 0 and hyp!= "0" : FeedContents.objects.create(feed=feed,contype="hyp",con=hyp)
    else:
        pass

def insertSmile(fid, uid):
    if (fid==None)|(uid==None):
        pass
    else:
        FeedSmile.objects.create(fid=Feed.objects.get(id=fid),uid=User.objects.get(id=uid))

def deleteSmile(fid=None, uid=None):
    if fid and uid:
        FeedSmile.objects.filter(fid=Feed.objects.get(id=fid),uid=User.objects.get(id=uid)).delete()

def insertReply(uid, fid, txt):
    if uid and fid and txt:
        reply = FeedReply.objects.create(user=User.objects.get(id=uid),feed=Feed.objects.get(id=fid),con=txt)
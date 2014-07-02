# -*- coding: utf-8 -*-
 
# Create your views here.
from redbomba.home.Func import *
from redbomba.home.models import Contents
from redbomba.home.models import Reply
from redbomba.home.models import Feed
from redbomba.home.models import Smile
from redbomba.home.models import League
from redbomba.home.models import GameLink
from redbomba.home.models import Check
from django import template
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.db.models import Max

######################################## Views ########################################
  
def read_Feed_pri(request) :
  try :
    uid = int(User.objects.get(username=request.GET["username"]).id)
  except Exception as e:
    uid = request.user.id
  try :
    len = int(request.GET["len"])
  except Exception as e:
    len = 0
  try :
    fid = int(request.GET["fid"])
  except Exception as e:
    fid = 0
  return HttpResponse(feedsorter("private", uid, len, fid, request))
  
def read_Feed_pub(request) :
  try :
    len = int(request.GET["len"])
  except Exception as e:
    len = 0
  try :
    fid = int(request.GET["fid"])
  except Exception as e:
    fid = 0
  return HttpResponse(feedsorter("public", request.user.id, len, fid, request))

def read_Feed_card(request) :
  try :
    len = int(request.GET["len"])
  except Exception as e:
    len = 0
  try :
    fid = int(request.GET["fid"])
  except Exception as e:
    fid = 0
  try :
    lid = int(request.GET["league_id"])
  except Exception as e:
    lid = 0
  return HttpResponse(feedsorter("card", lid, len, fid, request))
  
def setSmile(request):
  if request.user is None :
    return HttpResponse("error")
  else :
    if request.method=='GET':
      try :
        fid = request.GET["fid"]
        action = request.GET["action"]
        loc = request.GET["loc"]
        uid = request.user.id
        if action == "insert" :
          insertSmile(fid, uid)
        else :
          deleteSmile(fid, uid)
        if loc == "pri" :
          return HttpResponse(feedsorter("private", request.user.id, 1, fid, request))
        elif loc == "pub" :
          return HttpResponse(feedsorter("public", request.user.id, 1, fid, request))
        else :
          return HttpResponse("error")
      except Exception as e:
        return HttpResponse("error:")
    else :
      return HttpResponse("error")

def write_Feed(request):
  if request.method=='POST':
    try :
      action = request.POST["action"]
      uid = request.user.id
      uto = request.POST["uto"]
      utotype = request.POST["utotype"]
      feedtype = 1
      txt = request.POST["txt"]
      try :
        tag = request.POST["tag"]
      except Exception as e:
        tag = 0
      try :
        img = request.POST["img"]
        vid = request.POST["vid"]
        log = request.POST["log"]
        hyp = request.POST["hyp"]
      except Exception as e:
        img, vid, log, hyp = 0, 0, 0, 0
      if action == "insert" :
        insertFeed(uid, uto, utotype, feedtype, tag, img, txt, vid, log, hyp)
      else :
        pass
        #deleteFeed(fid, uid)
      try :
        loc = request.POST["loc"]
        return HttpResponse(feedsorter(loc, uto, 10, 0, request))
      except Exception as e:
        return HttpResponse(feedsorter("private", uto, 10, 0, request))
    except Exception as e:
      return HttpResponse("Input error:"+e.message)
  else :
    return HttpResponse("Input error")
    
def read_Reply(request) :
  try :
    len = int(request.GET["len"])
  except Exception as e:
    len = 0
  try :
    fid = int(request.GET["fid"])
  except Exception as e:
    fid = 0
  return HttpResponse(replysorter(request.user.id, len, fid))
      
def write_Reply(request):
  if request.method=='POST':
    try :
      action = request.POST["action"]
      uid = request.user.id
      fid = request.POST["fid"]
      txt = request.POST["txt"]
      if action == "insert" :
        insertReply(uid, fid, txt)
      else :
        pass
        #deleteFeed(fid, uid)
      return HttpResponse(replysorter(uid, 3, fid))
    except Exception as e:
      return HttpResponse("Input error:"+e.message)
  else :
    return HttpResponse("Input error")


def feedsorter(loc, uid, len, fid, request):
  
  if loc == "private" :
    try:
      user = User.objects.get(id=uid)
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
        try:
          c = Check.objects.get(fid=feedElem,uid=user)
        except Exception as e:
          Check.objects.create(fid=feedElem,uid=user)
        if i==len: break
        output = template.render(variables)
        val = val+output;
        i=i+1;
      return val
    except Exception as e:
      return e.message
  elif loc == "public" :
    try :
      user = User.objects.get(id=uid)
      reply = Reply.objects.filter(ufrom=uid).values_list('fid', flat=True)
      smile = Smile.objects.filter(uid=user).values_list('fid', flat=True)
      if fid==0 :
        feed = list(Feed.objects.filter())
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
    except Exception as e:
      return ""
  elif loc == "card" :
    try :
      user = League.objects.get(id=uid)
      if fid==0 :
        feed = Feed.objects.filter((Q(ufrom=user.id)&Q(ufromtype="l"))|(Q(uto=user.id)&Q(utotype="l"))).order_by("-date_updated")
      else :
        feed = Feed.objects.filter(id=fid).order_by("-date_updated")
      template = get_template('feed_card.html')
      val = ""
      i=0
      for feedElem in feed:
        variables = Context({
        'ele':fid,
        'fid' : feedElem.id,
        'uid' : uid,
        'ufrom': User.objects.get(id=feedElem.ufrom).username,
        'uto': League.objects.get(id=feedElem.uto).name,
        'ufromicon':User.objects.get(id=feedElem.ufrom).get_profile().user_icon,
        'date_updated':feedElem.get_time_diff(),
        'con_txt':Contents.objects.get(uto=feedElem.id, utotype='f', ctype='txt').con,
        'smile':list(Smile.objects.filter(fid=feedElem)),
        'isDone_smile':list(Smile.objects.filter(fid=feedElem,uid=request.user)),
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
    except Exception as e:
      return e.message
  else :
    return "Loc Error"

    
def replysorter(uid,len,fid):
  reply = Reply.objects.filter(fid=Feed.objects.get(id=fid)).order_by("-date_updated")
  template = get_template('reply_pri.html')
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


def insertFeed(uid, uto, utotype, feedtype, tag=0, img=0, txt=0, vid=0, log=0, hyp=0):
  if (uid==0)|(uto==0)|(utotype==0)|(txt==0) :
    pass
  else:
    feed = Feed.objects.create(ufrom=uid,ufromtype="u",uto=uto,utotype=utotype,feedtype=feedtype)
    Contents.objects.create(uto=feed.id,utotype='f',ctype="txt",con=txt)
    if tag!=0 or tag!='0' :
      Contents.objects.create(uto=feed.id,utotype='f',ctype="tag",con=tag)
    if img!=0 or img!='0' :
      Contents.objects.create(uto=feed.id,utotype='f',ctype="img",con=img)
    if vid!=0 or vid!='0' :
      Contents.objects.create(uto=feed.id,utotype='f',ctype="vid",con=vid)
    if log!=0 or log!='0' :
      Contents.objects.create(uto=feed.id,utotype='f',ctype="log",con=log)
    if hyp!=0 or hyp!='0' :
      Contents.objects.create(uto=feed.id,utotype='f',ctype="hyp",con=hyp)

def insertSmile(fid, uid):
  if (fid==None)|(uid==None):
    pass
  else:
    Smile.objects.create(fid=Feed.objects.get(id=fid),uid=User.objects.get(id=uid))
    
def deleteSmile(fid=0, uid=0):
  if (fid==0)|(uid==0):
    pass
  else:
    Smile.objects.filter(fid=Feed.objects.get(id=fid),uid=User.objects.get(id=uid)).delete()
    
def insertReply(uid, fid, txt):
  if (uid==0)|(fid==0)|(txt==0):
    pass
  else:
    reply = Reply.objects.create(ufrom=User.objects.get(id=uid),fid=Feed.objects.get(id=fid))
    Contents.objects.create(uto=reply.id,utotype='r',ctype="txt",con=txt)
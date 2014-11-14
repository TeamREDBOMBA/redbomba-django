# -*- coding: utf-8 -*-

# Create your views here.
from django.shortcuts import render
from redbomba.home.Func import *
from redbomba.home.models import *
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

######################################## Views ########################################

def getField(request) :
    if request.user is not None :
        query_g = GroupMember.objects.filter(user=request.user)
        groups = []
        for val in query_g:
            try :
                gm_count = GroupMember.objects.filter(group=val.group,is_active=1).count()
            except Exception as e:
                gm_count = 0
            groups.append({'gid':val.group,'count':gm_count})

        user = get_or_none(GroupMember,user=request.user)
        query_l = League.objects.filter(id__in=LeagueTeam.objects.filter(group=user.group).values_list('round__league', flat=True))
        leagues = []
        for val in query_l:
            ls = remakeLeagueState(val,user.uid)
            leagues.append(ls)
        context = {"groups":groups,"leagues":leagues}
        return render(request, 'field.html', context)
    return HttpResponse("error")

def write_Notification(request) :
    action = request.POST.get("action")
    if action == "read":
        noti = Notification.objects.filter(user=request.POST['uid'],date_read=-1).update(date_read=0)
    elif action == "check":
        if request.POST.get('loc') == "field" :
            noti = Notification.objects.filter(user=request.POST['uid'],action__icontains='League_').update(date_read=1)
        else :
            noti = Notification.objects.get(id=request.POST['nid'])
            noti.date_read = 1
            noti.save()
    return HttpResponse(' ')

def post_Notification(request) :
    uid = request.user
    gm = get_or_none(GroupMember,user=uid)
    if gm :
        lt = get_or_none(LeagueTeam,group=gm.group,is_complete=0)
        if lt :
            gms = GroupMember.objects.filter(group=lt.group,is_active=1).values_list('user', flat=True)
            gls = GameLink.objects.filter(user__in=gms)
            if len(gms)>=5 and (len(gms) == len(gls)) :
                lt.is_complete = 1
                lt.save()
                return HttpResponse(json.dumps({'gid':gm.group.id,'lid':lt.round.league.id,'action':'League_JoinLeague'}))
    return HttpResponse(0)

def read_Notification(request) :
    if request.method=='POST':
        try:
            template = get_template('noti.html')
            val = ""
            noti = Notification.objects.filter(user=request.user).order_by("-date_updated")[:8]
            for notiElem in noti:
                try:
                    user = request.user
                    variables = Context({
                        'user':user,
                        'ele':notiElem
                    })
                    output = template.render(variables)
                    val = val+output;
                except Exception as e:
                    val = e.message
            if val == "":
                val = u"새로운 소식이 없습니다."
            return HttpResponse(val)
        except Exception as e:
            return HttpResponse(u"새로운 소식이 없습니다."+e.message)
    else :
        return HttpResponse("새로운 소식이 없습니다.")
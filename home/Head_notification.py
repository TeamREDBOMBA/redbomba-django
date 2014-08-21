# -*- coding: utf-8 -*-

# Create your views here.
from redbomba.home.Func import *
from redbomba.home.models import *
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

######################################## Views ########################################

def write_Notification(request) :
    action = request.POST.get("action")
    if action == "read":
        noti = Notification.objects.filter(uid=request.POST['uid'],date_read=-1).update(date_read=0)
    elif action == "check":
        if request.POST.get('loc') == "field" :
            noti = Notification.objects.filter(uid=request.POST['uid'],tablename__icontains='league').update(date_read=1)
        else :
            noti = Notification.objects.get(id=request.POST['id'])
            noti.date_read = 1
            noti.save()
    return HttpResponse(' ')

def read_Notification(request) :
    if request.method=='POST':
        try:
            template = get_template('noti.html')
            val = ""
            noti = Notification.objects.filter(uid=request.user).order_by("-date_updated")[0:8]
            for notiElem in noti:
                try:
                    user = get_or_none(GroupMember,uid=request.user)
                    if user :
                        user = request.user
                    variables = Context({
                        'user':user,
                        'table':notiElem.tablename,
                        'state':NotificationMsg(notiElem, user),
                        'date':notiElem.get_time_diff(),
                        'this':notiElem
                    })
                    output = template.render(variables)
                    val = val+output;
                except Exception as e:
                    val = e.message
            if val == "":
                val = "새로운 소식이 없습니다."
            return HttpResponse(val)
        except Exception as e:
            return HttpResponse("새로운 소식이 없습니다."+e.message)
    else :
        return HttpResponse("새로운 소식이 없습니다.")

def NotificationMsg(notiElem, user):
    try :
        state = {}
        if notiElem.tablename == 'home_league' :
            con = League.objects.get(id=notiElem.contents)
            img = GroupMember.objects.get(uid=user.uid).gid.uid.get_profile().user_icon
            state['con'] = u"<b>%s</b>이 <b>%s</b>으로 <b>%s</b>에 참가하였습니다." %(user.gid.uid,user.gid.name,con.name)
            state['img'] = u"/static/img/icon/usericon_%d.jpg" %(img)
            state['imgurl'] = u"/static/img/icon/usericon_%d.jpg" %(img)
            state['this'] = con
        elif notiElem.tablename == 'home_smile' :
            con = Smile.objects.get(id=notiElem.contents)
            img = user.uid.get_profile.user_icon
            state['con'] = u"<b>%s</b>이 <b>%s</b>으로 <b>%s</b>에 참가하였습니다." %(user.gid.uid,user.gid.name,con.name)
            state['img'] = img
            state['imgurl'] = u"/static/img/icon/usericon_%d.jpg" %(img)
            state['this'] = con
        elif notiElem.tablename == 'home_group' :
            con = Group.objects.get(id=notiElem.contents)
            img = GroupMember.objects.get(uid=user.uid).gid.uid.get_profile().user_icon
            state['con'] = u"<b>%s</b>이 <b>%s</b>으로 초대하였습니다." %(user.gid.uid,user.gid.name)
            state['img'] = u"/static/img/icon/usericon_%d.jpg" %(img)
            state['imgurl'] = u"/static/img/icon/usericon_%d.jpg" %(img)
            state['this'] = con
        elif notiElem.tablename == 'home_leagueround' :
            con = LeagueRound.objects.get(id=notiElem.contents)
            img = Contents.objects.get(uto=con.league_id.id,utotype='l',ctype='img').con
            state['con'] = u"<b>%s</b>의 경기 일정이 발표되었습니다. <b>%s</b>의 일정을 확인해주세요." %(con.league_id.name,user.gid.name)
            state['img'] = img
            state['imgurl'] = img
            state['this'] = con
        elif notiElem.tablename == 'home_leaguematch' :
            con = LeagueMatch.objects.get(id=notiElem.contents)
            img = Contents.objects.get(uto=con.team_a.round.league_id.id,utotype='l',ctype='img').con
            state['con'] = u"<b>%s (Round%d)</b> 시작 30분 전 입니다. 모두 배틀페이지로 입장해주세요." %(con.team_a.round.league_id.name,con.team_a.round.round)
            state['img'] = img
            state['imgurl'] = img
            state['this'] = con
        return state
    except Exception as e:
        return None
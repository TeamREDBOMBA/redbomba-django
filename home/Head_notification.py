# -*- coding: utf-8 -*-

# Create your views here.
from django.shortcuts import render
from redbomba.home.Func import *
from redbomba.home.models import *
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

######################################## Views ########################################

def getField(request) :
    if request.user is not None :
        try :
            query_g = GroupMember.objects.filter(uid=request.user)
            groups = []
            for val in query_g:
                try :
                    gm_count = GroupMember.objects.filter(gid=val.gid,is_active=1).count()
                except Exception as e:
                    gm_count = 0
                groups.append({'gid':val.gid,'count':gm_count})

            user = GroupMember.objects.get(uid=request.user)
            query_l = League.objects.filter(id__in=LeagueTeam.objects.filter(group_id=user.gid).values_list('round__league_id', flat=True))
            leagues = []
            for val in query_l:
                ls = remakeLeagueState(val,user.uid)
                leagues.append(ls)
            context = {"groups":groups,"leagues":leagues}
            return render(request, 'field.html', context)
        except Exception as e:
            context = {"groups":None,"leagues":None}
            return render(request, 'field.html', context)
    return HttpResponse("error")

def write_Notification(request) :
    action = request.POST.get("action")
    if action == "read":
        noti = Notification.objects.filter(uid=request.POST['uid'],date_read=-1).update(date_read=0)
    elif action == "check":
        if request.POST.get('loc') == "field" :
            noti = Notification.objects.filter(uid=request.POST['uid'],action__icontains='League_').update(date_read=1)
        else :
            noti = Notification.objects.get(id=request.POST['nid'])
            noti.date_read = 1
            noti.save()
    return HttpResponse(' ')

def read_Notification(request) :
    if request.method=='POST':
        try:
            template = get_template('noti.html')
            val = ""
            noti = Notification.objects.filter(uid=request.user).order_by("-date_updated")[:8]
            for notiElem in noti:
                try:
                    user = request.user
                    variables = Context({
                        'user':user,
                        'state':NotificationMsg(notiElem, user),
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

def NotificationMsg(notiElem, user):
    try :
        state = None
        gm = get_or_none(GroupMember,uid=user)
        if notiElem.action == 'League_JoinLeague' :
            con = League.objects.get(id=notiElem.contents)
            img = gm.gid.uid.get_profile().user_icon
            state ={
                'con':u"<b>%s</b>님이 <b>%s</b>으로 <b>%s</b>에 참가하였습니다." %(gm.gid.uid,gm.gid.name,con.name),
                'img':u"/static/img/icon/usericon_%d.jpg" %(img),
                'imgurl':u"/static/img/icon/usericon_%d.jpg" %(img),
                'this':con
            }
        elif notiElem.action == 'League_RunMatchMaker' :
            con = LeagueRound.objects.get(id=notiElem.contents)
            img = Contents.objects.get(uto=con.league_id.id,utotype='l',ctype='img').con
            state ={
                'con':u"<b>%s</b>의 경기 일정이 발표되었습니다. <b>%s</b>의 일정을 확인해주세요." %(con.league_id.name,gm.gid.name),
                'img':img,
                'imgurl':img,
                'this':con
            }
        elif notiElem.action == 'League_StartMatch' :
            con = LeagueMatch.objects.get(id=notiElem.contents)
            img = Contents.objects.get(uto=con.team_a.round.league_id.id,utotype='l',ctype='img').con
            state ={
                'con':u"<b>%s (Round%d)</b> 시작 30분 전 입니다. 모두 배틀페이지로 입장해주세요." %(con.team_a.round.league_id.name,con.team_a.round.round),
                'img':img,
                'imgurl':img,
                'this':con
            }
        elif notiElem.action == 'Group_InviteMember' :
            con = Group.objects.get(id=notiElem.contents)
            img = gm.gid.uid.get_profile().user_icon
            state ={
                'con':u"<b>%s</b>님이 <b>%s</b>으로 초대하였습니다." %(gm.gid.uid,gm.gid.name),
                'img':u"/static/img/icon/usericon_%d.jpg" %(img),
                'imgurl':u"/static/img/icon/usericon_%d.jpg" %(img),
                'this':con
            }
        elif notiElem.action == 'Group_AskAddMember' :
            con = GroupMember.objects.get(gid__uid=notiElem.uid,uid=notiElem.contents)
            img = con.uid.get_profile().user_icon
            state ={
                'con':u"<b>%s</b>님이 <b>%s</b>에 가입 신청하였습니다." %(con.uid,gm.gid.name),
                'img':u"/static/img/icon/usericon_%d.jpg" %(img),
                'imgurl':u"/static/img/icon/usericon_%d.jpg" %(img),
                'this':con
            }
        elif notiElem.action == 'Group_AddMember' :
            con = GroupMember.objects.get(uid=notiElem.contents)
            img = con.uid.get_profile().user_icon
            state ={
                'con':u"<b>%s</b>님이 <b>%s</b>에 가입하였습니다." %(con.uid,gm.gid.name),
                'img':u"/static/img/icon/usericon_%d.jpg" %(img),
                'imgurl':u"/static/img/icon/usericon_%d.jpg" %(img),
                'this':con
            }
        elif notiElem.action == 'home_smile' :
            con = Smile.objects.get(id=notiElem.contents)
            img = gm.uid.get_profile.user_icon
            state ={
                'con':u"<b>%s</b>님이 <b>%s</b>으로 <b>%s</b>에 참가하였습니다." %(gm.gid.uid,gm.gid.name,con.name),
                'img':img,
                'imgurl':u"/static/img/icon/usericon_%d.jpg" %(img),
                'this':con
            }
        return state
    except Exception as e:
        return None
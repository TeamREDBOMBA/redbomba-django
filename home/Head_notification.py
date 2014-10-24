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

@csrf_exempt
def NotificationMsg(request):
    try :
        ele_action = request.GET.get("ele_action")
        ele_user = int(request.GET.get("ele_user"))
        ele_contents = request.GET.get("ele_contents")
        state = None
        user = get_or_none(User, id=ele_user)
        gm = get_or_none(GroupMember,user=user)
        if ele_action == 'League_JoinLeague' :
            con = League.objects.get(id=int(ele_contents))
            img = gm.group.leader.get_profile().user_icon
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s</b>님이 <b>%s</b>으로 <b>%s</b>에 참가하였습니다." %(gm.group.leader,gm.group.name,con.name),
                'icon':u"/media/%s" %(img),
                'link':u"/stats/?get=myarena"
            }
        elif ele_action == 'League_RunMatchMaker' :
            con = LeagueRound.objects.get(id=ele_contents)
            img = Contents.objects.get(uto=con.league.id,utotype='l',ctype='img').con
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s</b>의 경기 일정이 발표되었습니다. <b>%s</b>의 일정을 확인해주세요." %(con.league.name,gm.group.name),
                'icon':u"%s" %(img),
                'link':u"/stats/?get=myarena"
            }
        elif ele_action == 'League_StartMatch' :
            con = LeagueMatch.objects.get(id=ele_contents)
            img = Contents.objects.get(uto=con.team_a.round.league.id,utotype='l',ctype='img').con
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s (Round%d)</b> 시작 30분 전 입니다. 모두 배틀페이지로 입장해주세요." %(con.team_a.round.league.name,con.team_a.round.round),
                'icon':u"%s" %(img),
                'link':u"/battle/?round=%s" %(con.team_a.round.id)
            }
        elif ele_action == 'Group_InviteMember' :
            con = Group.objects.get(id=ele_contents)
            img = gm.group.leader.get_profile().user_icon
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s</b>님이 <b>%s</b>으로 초대하였습니다." %(gm.group.leader,gm.group.name),
                'icon':u"/media/%s" %(img),
                'link':u"/stats/"
            }
        elif ele_action == 'Group_AskAddMember' :
            con = GroupMember.objects.get(group__leader=user,user=ele_contents)
            img = con.user.get_profile().user_icon
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s</b>님이 <b>%s</b>에 가입 신청하였습니다." %(con.user,gm.group.name),
                'icon':u"/media/%s" %(img),
                'link':u"%d" %(con.group.id)
            }
        elif ele_action == 'Group_AddMember' :
            con = GroupMember.objects.get(user=ele_contents)
            img = con.user.get_profile().user_icon
            state ={
                'con':u"<b>%s</b>님이 <b>%s</b>에 가입하였습니다." %(con.user,gm.group.name),
                'icon':u"/media/%s" %(img),
                'link':u"/stats/"
            }
        elif ele_action == 'home_smile' :
            con = FeedSmile.objects.get(id=ele_contents)
            img = gm.user.get_profile().user_icon
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s</b>님이 <b>%s</b>으로 <b>%s</b>에 참가하였습니다." %(gm.group.leader,gm.group.name,con.name),
                'icon':u"/media/%s" %(img),
                'link':u"/"
            }
        Notification.objects.create(
                user=state['user'],
                action=state['action'],
                icon=state['icon'],
                contents=state['con'],
                link=state['user']
                )
        return HttpResponse(state)
    except Exception as e:
        return HttpResponse("ERROR:%s"%e.message)
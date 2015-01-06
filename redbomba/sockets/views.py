# -*- coding: utf-8 -*-

import json
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from redbomba.arena.models import League, LeagueRound, LeagueTeam, LeagueMatch
from redbomba.group.models import GroupMember, Chatting, Group
from redbomba.head.models import Notification
from redbomba.home.models import get_or_none

def setNotification(request):
    try :
        ele_action = request.GET.get("ele_action")
        ele_user = int(request.GET.get("ele_user"))
        ele_contents = request.GET.get("ele_contents")
        state = None
        user = get_or_none(User, id=ele_user)
        gm = get_or_none(GroupMember,user=user)
        if ele_action == 'League_JoinLeague' :
            con = League.objects.get(id=int(ele_contents))
            img = gm.group.leader.get_profile().src.url
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s</b>님이 <b>%s</b>으로 <b>%s</b>에 참가하였습니다." %(gm.group.leader,gm.group.name,con.name),
                'icon':u"%s" %(img),
                'link':u"/stats/?get=myarena"
            }
        elif ele_action == 'League_RunMatchMaker' :
            con = LeagueRound.objects.get(id=ele_contents)
            img = con.league.poster.url
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s</b>의 경기 일정이 발표되었습니다. <b>%s</b>의 일정을 확인해주세요." %(con.league.name,gm.group.name),
                'icon':u"%s" %(img),
                'link':u"/stats/?get=myarena"
            }
        elif ele_action == 'League_StartMatch' :
            con = LeagueMatch.objects.get(id=ele_contents)
            img = con.team_a.round.league.poster.url
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s (Round%d)</b> 시작 30분 전 입니다. 모두 배틀페이지로 입장해주세요." %(con.team_a.round.league.name,con.team_a.round.round),
                'icon':u"%s" %(img),
                'link':u"/battle/?round=%s" %(con.team_a.round.id)
            }
        elif ele_action == 'Group_InviteMember' :
            con = Group.objects.get(id=ele_contents)
            img = gm.group.leader.get_profile().src.url
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s</b>님이 <b>%s</b>으로 초대하였습니다." %(gm.group.leader,gm.group.name),
                'icon':u"%s" %(img),
                'link':u"/stats/"
            }
        elif ele_action == 'Group_AskAddMember' :
            con = GroupMember.objects.get(group__leader=user,user=ele_contents)
            img = con.user.get_profile().src.url
            state ={
                'user':user,
                'action':ele_action,
                'con':u"<b>%s</b>님이 <b>%s</b>에 가입 신청하였습니다." %(con.user,gm.group.name),
                'icon':u"%s" %(img),
                'link':u"%d" %(con.group.id)
            }
        elif ele_action == 'Group_AddMember' :
            con = GroupMember.objects.get(user=ele_contents)
            img = con.user.get_profile().src.url
            state ={
                'con':u"<b>%s</b>님이 <b>%s</b>에 가입하였습니다." %(con.user,gm.group.name),
                'icon':u"%s" %(img),
                'link':u"/stats/"
            }
        # elif ele_action == 'home_smile' :
        #     con = FeedSmile.objects.get(id=ele_contents)
        #     img = gm.user.get_profile().user_icon
        #     state ={
        #         'user':user,
        #         'action':ele_action,
        #         'con':u"<b>%s</b>님이 <b>%s</b>으로 <b>%s</b>에 참가하였습니다." %(gm.group.leader,gm.group.name,con.name),
        #         'icon':u"/media/%s" %(img),
        #         'link':u"/"
        #     }
        Notification.objects.create(
                user=state['user'],
                action=state['action'],
                icon=state['icon'],
                contents=state['con'],
                link=state['link']
                )
        return HttpResponse(state)
    except Exception as e:
        print "ERROR:%s"%e.message
        return HttpResponse("ERROR:%s"%e.message)

def sendNotification(request):
    state = []

    action = request.GET.get("action")

    if action == "League_JoinLeague" :
        group_id = request.GET.get("group_id")
        gms = GroupMember.objects.filter(group=group_id)
        if gms :
            for gm in gms:
                state.append({'user_id':gm.user.id})

    elif action == "League_RunMatchMaker" :
        league_id = request.GET.get("league_id")
        round_no = request.GET.get("round_no")

        lr = LeagueRound.objects.filter(league=league_id,round=round_no)
        lt_group = LeagueTeam.objects.filter(round__in=lr).values_list('group', flat=True)

        gms = GroupMember.objects.filter(group__in=lt_group)
        if gms :
            for gm in gms:
                state.append({'user_id':gm.user.id})

    return HttpResponse(json.dumps(state), content_type="application/json")

def setChatting(request):
    user_id = request.GET.get("user_id")
    group_id = request.GET.get("group_id")
    contents = request.GET.get("contents")

    if user_id and group_id and contents :
        Chatting.objects.create(user_id=user_id,group_id=group_id,con=contents)
        return HttpResponse("1")
    return HttpResponse("0")

@csrf_exempt
def sockets(request):
    if request.GET.get("mode") == "setNotification" :
        return setNotification(request)
    elif request.GET.get("mode") == "sendNotification" :
        return sendNotification(request)
    elif request.GET.get("mode") == "setChatting" :
        return setChatting(request)

    return HttpResponse('0')
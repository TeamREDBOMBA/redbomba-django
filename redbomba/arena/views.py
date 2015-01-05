# -*- coding: utf-8 -*-
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import Q, Min, Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from redbomba.arena.models import ArenaBanner, League, LeagueTeam, LeagueRound, LeagueMatch
from redbomba.group.models import GroupMember, Group
from redbomba.home.models import get_or_none, GameLink


def arena(request):
    if request.user.get_profile().is_pass_gamelink == 0 :
        return HttpResponseRedirect("/head/start/")
    top_banner = ArenaBanner.objects.all().order_by("-id")
    context = {
        'top_banner':top_banner,
        'user': request.user,
        'from':'/arena',
        'appname':'arena'
    }
    return render(request, 'arena.html', context)

def card_league(request) :
    leagues = League.objects.all().order_by("-id")
    context = {
        'leagues':leagues,
        'user': request.user
    }
    return render(request, 'card_league.html', context)

def card_league_large(request,lid=None):
    user = None
    if request.user.id :
        user = get_or_none(GroupMember,user=request.user)

    league = get_or_none(League,id=lid)

    if user :
        user_group = user.group
        user = user.user
    elif request.user.id :
        user = request.user
        user_group = None
    else :
        user = None
        user_group = None

    rule = league.rule
    if rule :
        rule = rule.replace("# ","",1)
        rule = rule.split("\n# ")
    con = {
        "concept":league.concept,
        "poster":league.poster.url,
        "rule":rule
    }

    groups = Group.objects.filter(id__in=LeagueTeam.objects.filter(round=get_or_none(LeagueRound,league=league,round=1),is_complete=1).values_list('group', flat=True))

    try:
        round1 = {"day":range((LeagueRound.objects.get(league=league,round=1).end - LeagueRound.objects.get(league=league,round=1).start).days+1)}
    except Exception as e:
        round1 = None

    rounds = LeagueRound.objects.filter(league=league)

    SR={}
    ER={}

    SR = LeagueRound.objects.filter(league=league).aggregate(min=Min('start'))
    SR['league'] = LeagueRound.objects.filter(league=league).annotate(Min('start'))[0]
    ER = LeagueRound.objects.filter(league=league).aggregate(max=Max('end'))
    ER['league'] = LeagueRound.objects.filter(league=league).annotate(Max('end'))[0]

    context = {
        'user': user,
        'user_group': user_group,
        'league':league,
        'contents':con,
        'groups':groups,
        'round1':round1,
        'rounds':rounds,
        'SR':SR,
        'ER':ER,
        'state':LeagueState(league,user)
        }
    return render(request, 'card_league_large.html', context)

def card_league_btn(request):
    user = None
    league = get_or_none(League, id=request.POST.get('lid'))
    if request.user.id is not None :
        user = get_or_none(User, id=request.POST.get('uid'))
        if user is None :
            user = request.user
    context = {
        'state':LeagueState(league,user)
    }
    return render(request, 'card_league_btn.html', context)

def LeagueState(league, user):

    no = "ERROR"

    #User State
    isFiveMem = IsFiveMem(league,user)                     # 1
    isFiveLink = IsFiveLink(league, user)           # 2
    isLeader = IsLeader(league,user)                       # 3
    isInGroup = IsInGroup(league,user)                     # 4

    #League State
    isStartApply = IsStartApply(league)             # 5
    isFullLeague = IsFullLeague(league)             # 6
    isEndApply = IsEndApply(league)                 # 8
    isFinishLeague = IsFinishLeague(league)         # 12
    isRun1stMathMaker = IsRun1stMathMaker(league)       # 9-2

    #User&League State
    isCompleteJoin = IsCompleteJoin(league, user)   # 7
    isRunMathMaker = IsRunMathMaker(isCompleteJoin) # 9-1
    isCanBattle = IsCanBattle(isRunMathMaker)       # 10
    isFinishMatch = IsFinishMatch(isCanBattle)      # 11

    #Etc State
    nowRound = NowRound(league)
    canMatchMaker = CanMatchMaker(nowRound)
    isHost = IsHost(league,user)
    getWinner = GetWinner(league,isFinishLeague)


    if isStartApply == None :
        no = -3
    elif (isLeader==None or (isFiveMem==None and isFiveLink==None and isInGroup==None)) and isStartApply!=None and isFullLeague==None and isCompleteJoin==None and isEndApply==None and isRunMathMaker==None :
        no = -2
    elif (isFiveMem == None or  isFiveLink==None) and isLeader!=None and isInGroup!=None and isStartApply!=None and isFullLeague==None and isCompleteJoin==None and isEndApply==None and isRunMathMaker==None :
        no = -1
    elif isFiveMem!=None and isFiveLink!=None and isLeader!=None and isInGroup!=None and isStartApply!=None and isFullLeague==None and isCompleteJoin==None and isEndApply==None and isRunMathMaker==None :
        no = 0
    elif isStartApply!=None and isCompleteJoin!=None and isRunMathMaker==None :
        no = 1
    elif isCompleteJoin!=None and isRunMathMaker!=None and isCanBattle==None :
        no = 2
    elif isCanBattle!=None and isFinishMatch==None :
        no = 3
    elif isRun1stMathMaker!=None and isFinishLeague == None :
        no = 4
    elif isFinishLeague != None :
        no = 5
    else :
        no = "Pass All"

    return {
        "no":no,
        "league":league,
        "user":user,
        "isFiveMem":isFiveMem,
        "isFiveLink":isFiveLink,
        "isLeader":isLeader,
        "isInGroup":isInGroup,
        "isHost":isHost,
        "isStartApply":isStartApply,
        "isFullLeague":isFullLeague,
        "isRun1stMathMaker":isRun1stMathMaker,
        "isFinishLeague":isFinishLeague,
        "isCompleteJoin":isCompleteJoin,
        "isRunMathMaker":isRunMathMaker,
        "isCanBattle":isCanBattle,
        "isFinishMatch":isFinishMatch,
        "canMatchMaker":canMatchMaker,
        "getWinner":getWinner,
        "nowRound":nowRound
    }

def IsFiveMem(league,user):
    group = user.get_profile().get_group(league.game)[0]
    if group :
        gm = group.get_members()
        if gm.count() >= 5 :
            return gm.count()
    return None

def IsFiveLink(league,user):
    group = user.get_profile().get_group(league.game)[0]
    if group :
        gm = group.get_members()
        gl = GameLink.objects.filter(user__contains=gm.values_list('user', flat=True),game=league.game)
        if gl :
            if gl.count() >= 5 :
                return gl.count()
    return None

def IsLeader(league,user):
    group = user.get_profile().get_group(league.game)[0]
    if group :
        if group.leader == user :
            return group.leader
    return None

def IsInGroup(league,user):
    group = user.get_profile().get_group(league.game)[0]
    if group :
        return group
    return None

def IsHost(league,user):
    host = league.host
    if host == user :
        return host == user
    return None

def IsStartApply(league):
    now = timezone.localtime(timezone.now())
    if league.start_apply <= now :
        return league.start_apply
    return None

def IsFullLeague(league):
    lt = LeagueTeam.objects.filter(round__league=league, round__round=1)
    if lt:
        if lt.count() >= league.max_team :
            return lt.count()
    return None

def IsEndApply(league):
    now = timezone.localtime(timezone.now())
    if league.end_apply < now :
        return league.end_apply
    return None

def IsFinishLeague(league):
    lr = LeagueRound.objects.filter(league=league).order_by("-round")
    if lr :
        lt = LeagueTeam.objects.filter(round__league=league)
        lm = LeagueMatch.objects.filter(Q(team_a__round=lr[0])|Q(team_b__round=lr[0])).order_by("-id")
        if lm :
            lastLM = lm[0]
            if lastLM.state == 10 :
                return lastLM
        if lt :
            pass
        else : return True
    return None

def IsRun1stMathMaker(league):
    lm = LeagueMatch.objects.filter(team_a__round__league=league, team_a__round__round=1)
    if lm :
        return lm[0]
    return None

def NowRound(league):
    lr = LeagueRound.objects.filter(league=league,is_finish=0).order_by("id")
    if lr :
        return lr[0]
    return None

def CanMatchMaker(nowRound):
    lm = LeagueMatch.objects.filter(Q(team_a__round=nowRound)|Q(team_b__round=nowRound))
    if lm :
        return None
    return nowRound

def IsCompleteJoin(league, user):
    group = user.get_profile().get_group(league.game)[0]
    if group :
        lt = LeagueTeam.objects.filter(group=group, round__league=league).order_by("-id")
        if lt :
            return lt[0]
    return None

def IsRunMathMaker(lt):
    if lt :
        lm = LeagueMatch.objects.filter(Q(team_a=lt)|Q(team_b=lt))
        if lm :
            return lm[0]
    return None

def IsCanBattle(lm):
    now = timezone.localtime(timezone.now())
    if lm :
        if lm.date_match-timedelta(minutes=30) <= now :
            return lm
    return None

def IsFinishMatch(lm):
    if lm :
        if lm.state == 10 :
            return lm
    return None

def GetWinner(league,lm):
    if lm and league :
        if lm != True :
            lm_all = LeagueMatch.objects.filter(Q(team_a__round__league=league)|Q(team_b__round__league=league)).order_by("-id")
            state = {"w1":None,"w2":None,"w3_1":None,"w3_2":None}
            if lm.result == "A" :
                state["w1"] = lm.team_a.group
                state["w2"] = lm.team_b.group
            else :
                state["w1"] = lm.team_b.group
                state["w2"] = lm.team_a.group

            if lm_all[1].result == "B" : state["w3_1"] = lm_all[1].team_a.group
            else : state["w3_1"] = lm_all[1].team_b.group
            if lm_all[2].result == "B" : state["w3_2"] = lm_all[2].team_a.group
            else : state["w3_2"] = lm_all[2].team_b.group

            return state
    return None
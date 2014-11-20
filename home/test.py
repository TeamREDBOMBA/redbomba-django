# -*- coding: utf-8 -*-

# Create your views here.

from django.views.decorators.csrf import csrf_exempt
from redbomba.home.Func import *
from redbomba.home.models import *
from redbomba.home.Arena_matchmaker import *


def makeUser(request):
    try:
        for u in range(0,20):
            username = "u%d"%u
            user = User.objects.create_user(
                username=username,
                password=username,
                email="%s@u.u"%username
            )
            user.is_active = True
            user.save()
            UserProfile.objects.create(user=user,user_icon="icon/usericon_1.jpg")
            PrivateCard.objects.create(user=user,contype='sys',con="""%s님. 만나서 반가워요!
이 곳은 %s님에게 관련된 소식만을 모아서 보여주는 활동 스트림 영역입니다.
레드밤바에서 다양한 활동을 즐겨보세요!"""%(user.username,user.username))
            GameLink.objects.create(
                user=user,
                game=get_or_none(Game,id=1),
                name='Tester',
                sid=1221495
            )
        return "makeUser success"
    except Exception as e:
        return "ERROR:%s"%e.message

def makeGroup(request):
    try:
        for g in range(0,4):
            groupname = "testGroup%d"%g
            group = Group.objects.create(
                name = groupname,
                nick = "g%d"%g,
                leader = User.objects.get(username="u%d"%(g*5)),
                game = Game.objects.get(name="League of Legends")
            )
        return "makeGroup success"
    except Exception as e:
        return "ERROR:%s"%e.message

def makeGroupMember(request):
    uno = 0
    try:
        for g in range(0,4):
            group = get_or_none(Group,nick = "g%d"%g)
            for n in range(0,5):
                GroupMember.objects.create(
                    group = group,
                    user = get_or_none(User,username="u%d"%uno),
                    order = n+1,
                    is_active = 1
                )
                uno = uno + 1
        return "makeGroupMember success"
    except Exception as e:
        return e.message

def makeLeague(request):
    try:
        now = timezone.localtime(timezone.now())
        league = League.objects.create(
            name = "Test League",
            host = get_or_none(User,id=31),
            game = get_or_none(Game,id=1),
            poster = "upload/files_1413436225/02.jpg",
            concept = "Test League",
            rule = "Test League",
            start_apply = now,
            end_apply = now + timedelta(hours=1),
            min_team = 4,
            max_team = 4
        )
        for i in range(1,4):
            LeagueReward.objects.create(
                league = league,
                name = "%d"%i,
                con = "%d"%(100/i)
            )
        for i in range(1,3):
            LeagueRound.objects.create(
                league=league,
                round = i,
                start = now + timedelta(hours=i),
                end = now + timedelta(hours=i+1)
            )
        return "makeLeague success"
    except Exception as e:
        return "ERROR:%s"%e.message

def makeLeagueTeam(request):
    try:
        lr = get_or_none(LeagueRound,round=1,league__name = "Test League")
        lr_start = lr.start + timedelta(hours=9)
        lr_end = lr.end + timedelta(hours=9)
        for g in range(0,4):
            LeagueTeam.objects.create(
                group = get_or_none(Group,name = "testGroup%d"%g),
                round = lr,
                feasible_time = "%d,%d"%(lr_start.hour,lr_end.hour),
            )
        return "makeLeagueTeam success"
    except Exception as e:
        return e.message

def startMatchMaker(request):
    try:
        lr = get_or_none(LeagueRound,round=1,league__name = "Test League")
        matchmaker(lr)
        return "makeLeagueTeam success"
    except Exception as e:
        return e.message


def delUser(request):
    try:
        for u in range(0,20):
            username = "u%d"%u
            User.objects.get(username=username).delete()
        return "delUser success"
    except Exception as e:
        return "ERROR:%s"%e.message

def delGroup(request):
    try:
        for g in range(0,4):
            groupname = "testGroup%d"%g
            Group.objects.get(name=groupname).delete()
        return "delGroup success"
    except Exception as e:
        return "ERROR:%s"%e.message

def delLeague(request):
    try:
        League.objects.get(name="Test League").delete()
        return "delLeague success"
    except Exception as e:
        return "ERROR:%s"%e.message

@csrf_exempt
def test(request):

    action = request.GET.get("action");

    if action == 'makeUser' : return HttpResponse(makeUser(request))
    elif action == 'makeGroup' : return HttpResponse(makeGroup(request))
    elif action == 'makeGroupMember' : return HttpResponse(makeGroupMember(request))
    elif action == 'makeLeague' : return HttpResponse(makeLeague(request))
    elif action == 'makeLeagueTeam' : return HttpResponse(makeLeagueTeam(request))
    elif action == 'startMatchMaker' : return HttpResponse(startMatchMaker(request))

    elif action == 'delUser' : return HttpResponse(delUser(request))
    elif action == 'delGroup' : return HttpResponse(delGroup(request))
    elif action == 'delLeague' : return HttpResponse(delLeague(request))

    elif action == 'ls' : return HttpResponse(LeagueState(get_or_none(League,name="Test League"),get_or_none(User,username="u0")))

    return HttpResponse("""
    <b>생성</b><br/>
    ?action=makeUser // 유저 20명 생성<br/>
    ?action=makeGroup // 4개 그룹 생성<br/>
    ?action=makeGroupMember // 4개 그룹에 유저 분배<br/>
    ?action=makeLeague // 대회 생성<br/>
    ?action=makeLeagueTeam // 4개 팀 생성<br/>
    ?action=startMatchMaker // 메치메이커 작동<br/>
    <br/><br/><b>삭제</b><br/>
    ?action=delUser // 유저 20명 삭제<br/>
    ?action=delGroup // 4개 그룹 삭제<br/>
    ?action=delLeague // 대회 삭제<br/>
    """)
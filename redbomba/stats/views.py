from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from redbomba.group.models import GroupMember
from redbomba.home.models import GameLink


def stats(request,username=None):
    target_uid = request.user
    if username :
        target_uid = User.objects.get(username=username)

    getval = request.GET.get('get','')
    gamelink = GameLink.objects.filter(user=target_uid)

    wait_group = GroupMember.objects.filter(user=target_uid,is_active=-1)

    context = {
        'user' : request.user,
        'target_user':target_uid,
        'wait_group':wait_group,
        'gamelink' : gamelink,
        'from' : '/stats/',
        'appname':'stats'
    }
    return render(request, 'stats.html', context)

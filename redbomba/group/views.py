from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from redbomba.group.models import Group, GroupMember
from redbomba.home.models import get_or_none


def card_group(request):
    groups = request.user.get_profile().get_group()
    context = {
        'user' : request.user,
        'groups':groups,
        'from' : '/stats/',
        'appname':'stats'
    }
    return render(request, 'group.html', context)

def card_group_large(request,gid=None):
    group = get_or_none(Group,id=gid)
    if group :
        groupmem = GroupMember.objects.filter(Q(group=group)&Q(is_active=1)).order_by("order")
        inviting = GroupMember.objects.filter(Q(group=group)&Q(is_active=0))
        waitting = GroupMember.objects.filter(Q(group=group)&Q(is_active=-1))

        isAdmin = Group.objects.filter(id=gid,leader=request.user)
        isMem = GroupMember.objects.filter(Q(group=group)&Q(user=request.user)&Q(is_active=1))
        isWait = GroupMember.objects.filter(Q(group=group)&Q(user=request.user)&Q(is_active=-1))
        isInv = GroupMember.objects.filter(Q(group=group)&Q(user=request.user)&Q(is_active=0))
        info = {"isAdmin":isAdmin, "isMem":isMem, "isWait":isWait, "isInv":isInv}

        context = {
            'user': request.user,
            'group':group,
            'groupmem':groupmem,
            'inviting':inviting,
            'waitting':waitting,
            'info':info,
            }
        return render(request, 'card_group_large.html', context)
    return HttpResponse("Request Error")
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.utils import simplejson
from redbomba.group.models import Group, GroupMember, Chatting
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

def card_group_members(request):
    action = request.POST.get('action')
    query = request.POST.get("text")
    group = get_or_none(Group,id=request.POST.get('gid'))

    if action == "insert" :
        query_g = GroupMember.objects.all().values_list('user', flat=True)
        users = User.objects.filter(~Q(id__in=query_g),Q(username__icontains=query))
    else :
        query_g = GroupMember.objects.filter(~Q(user=request.user),Q(group=group)).values_list('user', flat=True)
        users = User.objects.filter(Q(id__in=query_g),Q(username__icontains=query))

    context = {
        'users': users,
        'group':group,
        'mode':action
    }
    return render(request, 'card_group_members.html', context)

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

def card_group_large_order(request):
    if request.POST.get('action') == "get" :
        gid = request.POST.get('group')
        group = get_or_none(Group,id=gid)
        groupmem = GroupMember.objects.filter(Q(group=group)&Q(is_active=1)).order_by("order")

        context = {
            'groupmem':groupmem
        }
        return render(request, 'card_group_large_order.html', context)
    else :
        arr_list =  simplejson.loads(request.POST.get('memlist'))
        num = 0
        for al in arr_list:
            al = al.replace("div_","")
            gm = get_or_none(GroupMember,user=al)
            gm.order = num
            gm.save()
            num = num + 1
        return HttpResponse("Success")

def card_group_large_chatting(request):
    if request.user :
        len = int(request.POST.get("len",0))
        group = get_or_none(Group,id=request.POST.get("gid"))
        chatting = Chatting.objects.filter(group=group).order_by("-date_updated")
        val = ""
        for chatElem in chatting[:len] :
            username = chatElem.user.username
            con = chatElem.con
            if username == request.user.username:
                output = "<span class='username myname'>%s</span> : %s<br/>"%(username,con)
            elif username == "redbomba":
                output = "<span class='username myname'><font color='#e74c3c'>RED</font>BOMBA</span> : %s<br/>"%(con)
            else :
                output = "<span class='username'>%s</span> : %s<br/>"%(username,con)
            val = output+val
        return HttpResponse(val)
    return HttpResponse('ERROR')
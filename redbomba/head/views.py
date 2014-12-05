from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from redbomba.group.models import GroupMember
from redbomba.home.models import get_or_none


def head_userinfo(request):
    val = ""
    if request.method=='POST':
        uid = request.user
        gid =get_or_none(GroupMember,user=uid)

        if uid : uid = uid.id
        else: uid = 0

        if gid : gid = gid.id
        else: gid = 0

        val = val + "<uid>%d</uid>" %(uid)
        val = val + "<gid>%d</gid>" %(gid)
    else:
        val = "POST ERROR"
    return HttpResponse(val)
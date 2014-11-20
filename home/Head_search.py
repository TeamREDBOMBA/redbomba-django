# -*- coding: utf-8 -*-
 
# Create your views here.
from redbomba.home.Func import *
from redbomba.home.models import Group
from redbomba.home.models import GroupMember
from redbomba.home.models import GameLink
from django.contrib.auth.models import User
from django.shortcuts import render

######################################## Views ########################################

def getSearchBar(request) :
	users = []
	groups = []
	text = request.POST.get("text","")

	query_u = User.objects.filter(Q(username__icontains=text)|Q(id__in=GameLink.objects.filter(name__icontains=text).values_list('user', flat=True)))
	for val in query_u:
		gl = get_or_none(GameLink,user=val)
		gm = get_or_none(GroupMember,user=val)
		if gm : gm = gm.group
		users.append({'uid':val, 'gamelink':gl, 'group':gm})

	query_g = Group.objects.filter(Q(name__icontains=text)|Q(nick__icontains=text)|Q(leader__in=User.objects.filter(username__icontains=text)))
	for val in query_g:
		groups.append({'gid':val})

	context = {"users":users,"groups":groups}
	return render(request, 'searchbar_list.html', context)
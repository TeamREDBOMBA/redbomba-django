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
	if request.method=='POST':
		if request.user is not None :
			try:
			  text = request.POST["text"]
			except Exception as e:
			  text = ""

			query_u = User.objects.filter(Q(username__icontains=text)|Q(id__in=GameLink.objects.filter(name__icontains=text).values_list('uid', flat=True)))
			users = []
			for val in query_u:
				try:
					gl = GameLink.objects.get(uid=val)
				except Exception as e:
					gl = None
				try:
					gm = GroupMember.objects.get(uid=val).gid
				except Exception as e:
					gm = None
				users.append({'uid':val, 'gamelink':gl, 'group':gm})

			query_g = Group.objects.filter(Q(name__icontains=text)|Q(nick__icontains=text)|Q(uid__in=User.objects.filter(username__icontains=text)))
			groups = []
			for val in query_g:
				groups.append({'gid':val})

			context = {"users":users,"groups":groups}

			return render(request, 'searchbar_list.html', context)
		return HttpResponse("error")
	return HttpResponse("error")
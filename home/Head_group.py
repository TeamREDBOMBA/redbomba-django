# -*- coding: utf-8 -*-

# Create your views here.
from redbomba.home.Func import *
from redbomba.home.models import Game, Chatting
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils import simplejson

######################################## Views ########################################


def getGroup(request):
    if request.POST.get('username') :
        uid = get_or_none(User,username=request.POST.get('username'))
        if uid :
            uid = uid.id
    else :
        uid = request.user.id
    return HttpResponse(groupsorter(uid, request))

def getGroupMember(request):
    if request.method=='POST':
        try :
            if request.user.username != request.POST.get('username') :
                uid = User.objects.get(username=request.POST.get('username')).id
            else :
                uid = request.user.id
            gid = request.POST.get("gid")
            return HttpResponse(groupmembersorter(uid,gid))
        except Exception as e:
            return HttpResponse("Input error:"+e.message)
    else :
        return HttpResponse("Input error")

def getGroupList(request):
    if request.method=='POST':
        uid = request.user
        action = request.POST["action"]
        try:
            text = request.POST["text"]
        except Exception as e:
            text = ""
        if action == "insert" :
            query_g = GroupMember.objects.all().values_list('user', flat=True)
            query_u = User.objects.filter(~Q(id__in=query_g),Q(username__icontains=text))
            query = []
            for val in query_u:
                query.append({'id':val.id, 'username':val.username, 'user_icon':"/media/%s"%(val.get_profile().get_icon())})
            context = { 'user': query, 'gid':GroupMember.objects.get(user=uid).group.id, 'mode':action }
            return render(request, 'groupmemlist.html', context)
        else :
            query_g = GroupMember.objects.filter(~Q(user=uid),Q(group=Group.objects.get(id=request.POST["gid"]))).values_list('user', flat=True)
            query_u = User.objects.filter(Q(id__in=query_g),Q(username__icontains=text))
            query = []
            for val in query_u:
                query.append({'id':val.id, 'username':val.username, 'user_icon':"/media/%s"%(qval.get_profile().get_icon())})
            context = { 'user': query, 'gid':GroupMember.objects.get(user=uid).group.id, 'mode':action }
            return render(request, 'groupmemlist.html', context)
    else:
        return HttpResponse("Request Error")

def getGroupInfo(request):
    if request.method=='POST':
        gid = request.POST['group']
        try:
            group = Group.objects.get(id=gid)
            groupmem = GroupMember.objects.filter(Q(group=group)&Q(is_active=1)).order_by("order")
            inviting = GroupMember.objects.filter(Q(group=group)&Q(is_active=0))
            waitting = GroupMember.objects.filter(Q(group=group)&Q(is_active=-1))
        except Exception as e:
            group = None
            groupmem = None
            inviting = None
            waitting = None
        try:
            isAdmin = Group.objects.filter(id=gid,leader=request.user).count()
            isMem = GroupMember.objects.filter(Q(group=group)&Q(user=request.user)&Q(is_active=1)).count()
            isWait = GroupMember.objects.filter(Q(group=group)&Q(user=request.user)&Q(is_active=-1)).count()
            isInv = GroupMember.objects.filter(Q(group=group)&Q(user=request.user)&Q(is_active=0)).count()
            info = {"isAdmin":isAdmin, "isMem":isMem, "isWait":isWait, "isInv":isInv}
        except Exception as e:
            info = {"isAdmin":0, "isMem":0, "isWait":0, "isInv":0}
        context = {
            'user': request.user,
            'group':group,
            'groupmem':groupmem,
            'inviting':inviting,
            'waitting':waitting,
            'info':info,
            }
        return render(request, 'group_info.html', context)
    else:
        return HttpResponse("Request Error")

def getGroupInfoOrder(request):
    if request.method=='POST':
        if request.POST['action'] == "get" :
            gid = request.POST['group']
            try:
                group = Group.objects.get(id=gid)
                groupmem = GroupMember.objects.filter(Q(group=group)&Q(is_active=1)).order_by("order")
            except Exception as e:
                groupmem = None

            context = {
                'groupmem':groupmem
            }
            return render(request, 'group_info_order.html', context)
        else :
            arr_list =  simplejson.loads(request.POST['memlist'])
            num = 0
            for al in arr_list:
                al = al.replace("div_","")
                gm = GroupMember.objects.get(user=al)
                gm.order = num
                gm.save()
                num = num + 1
            return HttpResponse("Success")
    else:
        return HttpResponse("Request Error")

def write_Group(request):
    if request.method=='POST':
        action = request.POST["action"]
        if action == "insert" :
            group = Group.objects.create(
                name=request.POST["name"],
                nick=request.POST["nick"],
                leader=request.user,
                group_icon='common.png',
                game=Game.objects.get(name=request.POST["game"])
            )
            try:
                GroupMember.objects.get(
                    group=group,
                    user=request.user,
                    is_active=1
                )
            except Exception as e:
                GroupMember.objects.create(
                    group=group,
                    user=request.user,
                    is_active=1
                )
            Chatting.objects.create(
                group=group,
                user=User.objects.get(id=1),
                con='"%s" 게이밍 그룹이 성공적으로 개설 되었습니다.'%(group.name)
            )
            return HttpResponse(group.id)
        else :
            gid = request.POST["gid"]
            group = Group.objects.get(id=gid)
            GroupMember.objects.filter(group=group).delete()
            group.delete()
            return HttpResponse("Success")
    else:
        return HttpResponse("error")

def setGroupMember(request):
    if request.method=='POST':
        action = request.POST["action"]
        user = request.user
        try:
            user = User.objects.get(username=request.POST["username"])
        except Exception as e:
            user = request.user
        if action == "yes" :
            group = Group.objects.get(id=request.POST["gid"])
            gm = GroupMember.objects.get(Q(group=group)&Q(user=user)&~Q(is_active=1))
            gm.is_active = 1
            gm.save()
        else:
            group = Group.objects.get(id=request.POST["gid"])
            GroupMember.objects.filter(Q(group=group)&Q(user=user)&~Q(is_active=1)).delete()
        return HttpResponse("Success")
    else:
        return HttpResponse("error")

def setGroupList(request):
    if request.method=='POST':
        try:
            action = request.POST["action"]
            group = Group.objects.get(id=request.POST["gid"])
            if action == "Join" :
                try:
                    gm=GroupMember.objects.get(group=group,user=request.user)
                except Exception as e:
                    gm=GroupMember.objects.create(group=group,user=request.user,is_active=-1)
            elif action == "Quit" :
                GroupMember.objects.filter(group=group,user=request.user).delete()
            elif group == Group.objects.get(user=request.user) :
                user = User.objects.get(username=request.POST["username"])
                if action == "insert" :
                    try:
                        gm=GroupMember.objects.get(group=group,user=user)
                    except Exception as e:
                        gm=GroupMember.objects.create(group=group,user=user,is_active=0)
                elif action == "changeLeader" :
                    if GroupMember.objects.filter(group=group,user=user).count() :
                        group.user = user
                        group.save()
                else:
                    GroupMember.objects.filter(group=group,user=user).delete()
            else:
                return HttpResponse("error")
            return HttpResponse("Success")
        except Exception as e:
            return HttpResponse("error")
    else:
        return HttpResponse("error")

def getChatting(request):
    if request.user :
        len = int(request.POST.get("len",0))
        group = Group.objects.get(name=request.POST["group_name"])
        chatting = Chatting.objects.filter(group=group).order_by("-date_updated")
        val = ""
        i=0
        for chatElem in chatting:
            if i==len: break
            username = chatElem.user.username
            con = chatElem.con
            if username == request.user.username:
                output = "<span class='username myname'>%s</span> : %s<br/>"%(username,con)
            elif username == "redbomba":
                output = "<span class='username myname'><font color='#e74c3c'>RED</font>BOMBA</span> : %s<br/>"%(con)
            else :
                output = "<span class='username'>%s</span> : %s<br/>"%(username,con)
            val = output+val
            i=i+1
        return HttpResponse(val)
    return HttpResponse('ERROR')

def groupsorter(uid, request):
    val = ""
    query_gm = GroupMember.objects.filter(Q(user=User.objects.get(id=uid))&~Q(is_active=-1))
    if query_gm :
        template = get_template('group.html')
        for gmElem in query_gm:
            query_group = Group.objects.get(id=gmElem.group.id)
            if query_group.leader.id == gmElem.user.id:
                host = "host"
            else :
                host = ""
            variables = Context({
                'group' : query_group,
                'is_active' : gmElem.is_active,
                'host':host,
                'target_user':uid,
                'user':request.user
            })
            output = template.render(variables)
            val = val+output;
    else :
        template = get_template('groupadd.html')
        variables = Context({
            'target_user':uid,
            'user':request.user
        })
        output = template.render(variables)
        val = output;
    return val

def groupmembersorter(uid,gid):
    val = ""
    if GroupMember.objects.get(Q(group=Group.objects.get(id=gid))&Q(user=User.objects.get(id=uid))&~Q(is_active=-1)) :
        query_gm = GroupMember.objects.filter(Q(group=Group.objects.get(id=gid))&~Q(is_active=-1)).order_by('user')
        template = get_template('groupmember.html')
        for gmElem in query_gm:
            if Group.objects.get(id=gmElem.group.id).leader.id == gmElem.user.id:
                host = "host"
            else :
                host = ""
            user = User.objects.get(id=gmElem.user.id)
            variables = Context({
                'group_user' : user,
                'group_active':gmElem.is_active,
                'is_active' : GroupMember.objects.get(group=Group.objects.get(id=gid),user=User.objects.get(id=uid)).is_active,
                'host' : host,
                'uinfo':user.get_profile
            })
            output = template.render(variables)
            val = val+output;
    else :
        val = None
    return val

def fncGroupName(request):
    groupname = request.GET["name"]
    res = get_or_none(Group,name=groupname)
    if res==None:
        return HttpResponse("")
    else :
        return HttpResponse("%s 은(는) 이미 사용 중 입니다." %(groupname))

def fncGroupNick(request):
    groupnick = request.GET["nick"]
    print str(unicode(groupnick))
    res = get_or_none(Group,nick=groupnick)
    if res==None:
        return HttpResponse("")
    else :
        return HttpResponse("%s 은(는) 이미 사용 중 입니다." %(groupnick))
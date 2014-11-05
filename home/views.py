# -*- coding: utf-8 -*-

# Create your views here.
import sys
from redbomba.home.Func import *
from redbomba.home.Arena_league import *
from redbomba.home.Arena_matchmaker import *
from redbomba.home.Battle import *
from redbomba.home.Feed import *
from redbomba.home.Head_group import *
from redbomba.home.Head_notification import *
from redbomba.home.Head_search import *
from redbomba.home.Login_join import *
from redbomba.home.Login_login import *
from redbomba.home.Main import *
from redbomba.home.Mobile import *
from redbomba.home.Stats_gamelink import *
from redbomba.home.Stats_myarena import *
from redbomba.home.test import *
from django.utils import timezone

reload(sys)
sys.setdefaultencoding('utf-8')

def home(request):
    context = ''
    if request.GET.get('msg'):
        context= errorMsg(request.GET.get('msg'))
        context['site'] = request.GET.get('site')
    return render(request, 'login.html', context)

def main(request):
    try:
        getval = request.GET.get('get','')
        link = request.GET.get("link")
        if link:
            if link.startswith('league') :
                link = link.replace("league","")
                link = get_or_none(League,id=link)
                link = {"id":link.id,"img":Contents.objects.get(uto=link.id,utotype='l',ctype='img').con,"title":link.name,"inf":Contents.objects.get(uto=link.id,utotype='l',ctype='txt').con,"type":"league"}

        gl = request.user.get_profile().get_gamelink()
        if gl.count() :
            gl_h = 100.0/int(gl.count())
        else :
            gl_h = 0

        try :
            group = request.user.get_profile().get_group().group
            groupmem = GroupMember.objects.filter(group=group)
        except Exception as e:
            group = None
            groupmem = None

        get_group = request.GET.get('group')
        context = {
            'user': request.user,
            'group':group,
            'groupmem':groupmem,
            'get_group':get_group,
            'getval':getval,
            'gamelink':gl,
            'height':gl_h,
            'from':'/',
            'link':link
        }
    except Exception as e:
        context = {'user': request.user}
    return render(request, 'main.html', context)

def stats(request,username=None):
    try:
        myuid = request.user
        if username :
            target_uid = User.objects.get(username=username)
        else :
            target_uid = myuid

        getval = request.GET.get('get','')
        gl = GameLink.objects.filter(user=target_uid)

        wait_group = GroupMember.objects.filter(user=target_uid,is_active=-1)

        group = GroupMember.objects.filter(Q(user=target_uid)&~Q(is_active=-1))
        if group.count() :
            group = group[0].group
            groupmem = GroupMember.objects.filter(Q(group=group)&~Q(is_active=-1))
        else : groupmem = None

        get_group = request.GET.get('group',None)

        context = {
            'user' : request.user,
            'uinfo':request.user.get_profile,
            'target_user':target_uid,
            'group':group,
            'groupmem':groupmem,
            'get_group':get_group,
            'wait_group':wait_group,
            'gamelink' : gl,
            'getval':getval,
            'from' : '/stats/'
        }
    except Exception as e:
        context = {'user': request.user}
    return render(request, 'stats.html', context)

def arena(request):
    try:
        getval = request.GET.get('get')

        group = GroupMember.objects.filter(Q(user=request.user)&~Q(is_active=-1))
        if group.count() :
            group = group[0].group
            groupmem = GroupMember.objects.filter(Q(group=group)&~Q(is_active=-1))
        else : groupmem = None

        get_group = request.GET.get('group')

        is_pass1 = get_or_none(Tutorial,user=request.user)
        if is_pass1 : is_pass1 = int(is_pass1.is_pass1)

        state = {"is_pass1":is_pass1}

        context = {
            'user': request.user,
            'uinfo' : request.user.get_profile,
            'group':group,
            'groupmem':groupmem,
            'get_group':get_group,
            'getval':getval,
            'state':state,
            'from' : '/arena/'
        }
    except Exception as e:
        context = {'user': request.user}
    return render(request, 'arena.html', context)

def page_for_link(request,lid=None,gid=None):
    if lid :
        lid = int(lid)
        lid = get_or_none(League,id=lid)
    if gid :
        gid = int(gid)
        gid = get_or_none(Group,id=gid)

    user, user_profile = None, None

    if request.user.id :
        user = request.user
        user_profile = request.user.get_profile

    group = GroupMember.objects.filter(Q(user=user)&~Q(is_active=-1))
    if group.count() :
        group = group[0].group
        groupmem = GroupMember.objects.filter(Q(group=group)&~Q(is_active=-1))
    else : groupmem = None

    get_group = request.GET.get('group')

    if lid:
        con = {'text':'','img':''}
        con['text']=lid.concept
        con['img']=lid.poster
        context = {
            'user': user,
            'uinfo' : user_profile,
            'group':group,
            'groupmem':groupmem,
            'lid':lid, 'con':con,
            'get_group':get_group,
            'from' : '/league/'
        }
    elif gid :
        con = {'text':'','img':''}
        con['text']="%s 그룹에 당신을 초대합니다."%(gid.name)
        con['img']=gid.group_icon
        context = {
            'user': user,
            'uinfo' : user_profile,
            'group':gid,
            'groupmem':groupmem,
            'gid':gid, 'con':con,
            'get_group':get_group,
            'from' : '/league/'
        }
    else :
        context = {'user': request.user}
    return render(request, 'page_for_link.html', context)

@csrf_exempt
def file(request):
    action = request.GET.get("action");
    if action == None :
        return HttpResponse("""
        <form enctype='multipart/form-data' method='post' action='/file/?action=output'>
        <input type='file' name='file' id='file'/>
        <input type='submit'>
        </form>
        """)
    return HttpResponse(upload(request))
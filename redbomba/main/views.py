# -*- coding: utf-8 -*-
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from datetime import datetime
from django.utils import timezone

from forms import PostImageForm

from redbomba.arena.models import LeagueMatch
from redbomba.feed.models import Feed, FeedReply
from redbomba.group.models import Group, GroupMember
from redbomba.home.models import get_or_none, GameLink
from redbomba.main.models import GlobalCard, PrivateCard, Tag, Post, PostImage, PostReply, PostSmile, Follow, NewsFeed


def main(request):
    try:
        if request.user.get_profile().tutorial_phase == 0 :
            return HttpResponseRedirect("/head/start/")
        if request.user.get_profile().tutorial_phase == 1:
            return HttpResponseRedirect("/head/invite/")
        if request.user.get_profile().tutorial_phase == 2:
            return HttpResponseRedirect("/head/complete/")

        if 'rsid' in request.session:
            for rsid in request.session['rsid']:
                if rsid in request.session:
                    del request.session[rsid]

        request.session['loadtime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        members = GroupMember.objects.filter(user=request.user)
        groups = []
        gamelink = GameLink.objects.filter(user=request.user)

        for m in members:
            groups.append(m.group)

        context = {
            'gamelink':gamelink,
            'user': request.user,
            'from':'/',
            'appname':'main',
            'profile': request.user.get_profile(),
            'groups': groups,
        }
    except Exception as e:
        context = {'user': request.user}
    return render(request, 'main.html', context)


def get_followers(user):
    followers_id = Follow.objects.filter(tuser=user).values_list('fuser', flat=True)
    followers = []

    for follower_id in followers_id:
        followers.append(User.objects.get(id=follower_id))

    return followers

def new_post(request):
    user = request.user
    content = request.POST.get('content')
    tags = request.POST.getlist('tags[]')
    gametag = request.POST.get('gametag')
    video = request.POST.get('video')

    post = Post.objects.create(user=user, content=content, video=video)

    for tag in tags:
        t = get_or_none(Tag, name=tag)
        if t:
            post.tag.add(t)
        else:
            t = Tag.objects.create(name=tag)
            post.tag.add(t)

    t = get_or_none(Tag, name=gametag)
    if t:
        post.tag.add(t)
    else:
        t = Tag.objects.create(name=gametag)
        post.tag.add(t)

    post.save()

    followers = get_followers(user)

    for follower in followers:
        feed = NewsFeed.objects.create(subscriber=follower, post=post, publisher=user, reason=0)
        feed.save()

    feed = NewsFeed.objects.create(subscriber=user, post=post, publisher=user, reason=0)
    feed.save()

    return HttpResponse(post.id)


@csrf_exempt
def add_post_image(request, pid):
    #if request.method == 'POST':
    form = PostImageForm(request.POST, request.FILES)
        #if form.is_valid():
    post = Post.objects.get(id=pid)
    image = PostImage(post=post, src=request.FILES[u'files[]'])
    image.save()

    return HttpResponse('성공')

#    return HttpResponse('오류임')


def new_reply(request):
    user = request.user
    post = Post.objects.get(id=int(request.POST.get('postid')))
    content = request.POST.get('content')

    reply = PostReply.objects.create(user=user, content=content, post=post)
    reply.save()

    followers = get_followers(user)

    for follower in followers:
        feed = NewsFeed.objects.get(subscriber=follower, post=post)

        if feed:
            feed.publisher = user
            feed.reason = 2
        else:
            feed = NewsFeed.objects.create(subscriber=follower, post=post, publisher=user, reason=2)

        feed.save()

    return HttpResponse("OK")



def new_smile(request):
    user = request.user
    post = Post.objects.get(id=request.POST.get('postid'))

    smile = PostSmile.objects.filter(user=user, post=post)

    if smile:
        return HttpResponse("duplicated")
    else:
        smile = PostSmile.objects.create(user=user, post=post)
        smile.save()

        followers = get_followers(user)

        for follower in followers:
            feed = NewsFeed.objects.get(subscriber=follower, post=post)

            if feed:
                feed.publisher = user
                feed.reason = 1
            else:
                feed = NewsFeed.objects.create(subscriber=follower, post=post, publisher=user, reason=1)

            feed.save()

        return HttpResponse("OK")

def del_smile(request):
    user = request.user
    post = Post.objects.get(id=request.POST.get('postid'))

    smile = PostSmile.objects.filter(user=user, post=post)

    if smile:
        smile.delete()

        followers = get_followers(user)

        for follower in followers:
            feed = NewsFeed.objects.filter(subscriber=follower, post=post, publisher=user, reason=1)

            if feed:
                feed.delete()

        return HttpResponse("OK")
    else:
        return HttpResponse("notfound")

def follow(request):
    user = request.user
    tuser = User.objects.get(id=request.POST.get('userid'))

    follow = Follow.objects.filter(fuser=user, tuser=tuser)

    if follow:
        return HttpResponse("duplicated")
    else:
        follow = Follow.objects.create(fuser=user, tuser=tuser)
        follow.save()
        return HttpResponse("OK")

def unfollow(request):
    user = request.user
    tuser = User.objects.get(id=request.POST.get('userid'))

    follow = Follow.objects.filter(fuser=user, tuser=tuser)

    if follow:
        follow.delete()
        return HttpResponse("OK")
    else:
        return HttpResponse("notfound")


def load_newsfeed(request):
    if ('loadtime' not in request.session):
        request.session['loadtime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    feeds = NewsFeed.objects.filter(subscriber=request.user, date_updated__lt=request.POST.get('loadtime')).order_by("-date_updated")

    if feeds:
        feed = feeds[0]
        post = feed.post

        replys = PostReply.objects.filter(post=post).order_by("-date_updated")
        smiles = PostSmile.objects.filter(post=post)
        my_smile = smiles.filter(user=request.user)
        num_replys = 0
        reply = None
        replytime = None
        images = PostImage.objects.filter(post=post)

        if replys:
            num_replys = len(replys)
            reply = replys[0]

            if 'rsid' not in request.session:
                request.session['rsid'] = []

            rsid = 'replyof%d' % post.id
            request.session['rsid'].append(rsid)
            request.session[rsid] = timezone.localtime(reply.date_updated).strftime("%Y-%m-%d %H:%M:%S")
            replytime = request.session[rsid]

        context = {
            'post': post,
            'num_replys': num_replys,
            'num_smiles': len(smiles),
            'my_smile': my_smile,
            'reply': reply,
            'postdatetime': timezone.localtime(post.date_updated).strftime("%Y-%m-%d %H:%M:%S"),
            'feeddatetime': timezone.localtime(feed.date_updated).strftime("%Y-%m-%d %H:%M:%S"),
            'replytime': replytime,
            'publisher': feed.publisher,
            'reason': feed.reason,
            'images': images
        }

    else:
        context = {
            'post': None,
            'datetime': request.session['loadtime']
        }

    return render(request, 'post.html', context)



@csrf_exempt
def load_reply(request):
    if 'rsid' not in request.session:
        request.session['rsid'] = []

    rsid = 'replyof%s' % request.POST.get('postid')

    if rsid not in request.session:
        request.session['rsid'].append(rsid)
        request.session[rsid] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    last_time = request.session[rsid]

    post = Post.objects.get(id=request.POST.get('postid'))
    replys = PostReply.objects.filter(post=post, date_updated__lt=last_time).order_by("-date_updated")

    if not replys:
        return HttpResponse("not more")
    else:
        num_replys = len(replys)
        if num_replys > 5:
            num_replys = 5

        replys = replys[:num_replys]
        replys.reverse()
        context = {
            'replys': replys
        }
        request.session[rsid] = timezone.localtime(replys[0].date_updated).strftime("%Y-%m-%d %H:%M:%S")
        return render(request, 'post_reply.html', context)

def load_post_profile(request):
    post = Post.objects.get(id=request.POST.get('id'))
    follow = Follow.objects.filter(fuser=request.user, tuser=post.user)

    context = {
        'user': request.user,
        'profile_user': post.user,
        'follow': follow
    }

    return render(request, 'popover_profile.html', context)

def load_reply_profile(request):
    reply = PostReply.objects.get(id=request.POST.get('id'))
    follow = Follow.objects.filter(fuser=request.user, tuser=reply.user)

    context = {
        'user': request.user,
        'profile_user': reply.user,
        'follow': follow
    }

    return render(request, 'popover_profile.html', context)

def card_global(request):
    news = []
    globalcards = GlobalCard.objects.filter().order_by("-date_updated")
    if globalcards :
        for gf in globalcards :
            news.append({"id":gf.id,"title":gf.title,"txt":gf.con,"img":{"src":"%s"%(gf.src.url),"focusx":gf.focus_x,"focusy":gf.focus_y},"user":gf.user})
        context = {'user':request.user,'news':news}
        return render(request, 'card_global.html', context)
    return HttpResponse("")

def card_global_large(request, fid=None):
    if fid :
        gf = get_or_none(GlobalCard,id=fid)
        context = {
            'user':request.user,
            'news':gf
        }
        return render(request, 'card_global_large.html', context)
    return HttpResponse(None)

def card_private(request):
    user = request.user
    group = user.get_profile().get_group()
    news = []

    mygroup = GroupMember.objects.filter(user=user).values_list('group', flat=True)
    if mygroup :
        gm = GroupMember.objects.filter(Q(group__in=mygroup)&~Q(user=user))
        if gm :
            for value in gm :
                news.append({'self':value,'type':'groupmember','date':value.date_updated})

    feeds = Feed.objects.filter(user=user)
    for feed in feeds :
        reply = feed.reply.filter(~Q(user=user)).order_by("-date_updated")
        if reply :
            for value in reply :
                news.append({'self':value,'type':'reply','date':value.date_updated})

    pc = PrivateCard.objects.filter(user=user).order_by("-date_updated")
    if pc :
        for value in pc :
            news.append({'self':value,'type':'system','date':value.date_updated})

    lm = LeagueMatch.objects.filter(Q(team_a__group__in=group)|Q(team_b__group__in=group)).filter(state=10).order_by("-date_updated")
    if lm :
        for value in lm :
            news.append({'self':value,'type':'leaguematch','date':value.date_updated})

    news.sort(key=lambda item:item['date'], reverse=True)
    context = {'user':user,'news':news}
    return render(request, 'card_private.html', context)


def load_stream(request):
    user = request.user
    group = user.get_profile().get_group()
    news = []

    mygroup = GroupMember.objects.filter(user=user).values_list('group', flat=True)
    if mygroup :
        gm = GroupMember.objects.filter(Q(group__in=mygroup)&~Q(user=user))
        if gm :
            for value in gm :
                news.append({'self':value,'type':'groupmember','date':value.date_updated})

    feeds = Feed.objects.filter(user=user)
    for feed in feeds :
        reply = feed.reply.filter(~Q(user=user)).order_by("-date_updated")
        if reply :
            for value in reply :
                news.append({'self':value,'type':'reply','date':value.date_updated})

    pc = PrivateCard.objects.filter(user=user).order_by("-date_updated")
    if pc :
        for value in pc :
            news.append({'self':value,'type':'system','date':value.date_updated})

    lm = LeagueMatch.objects.filter(Q(team_a__group__in=group)|Q(team_b__group__in=group)).filter(state=10).order_by("-date_updated")
    if lm :
        for value in lm :
            news.append({'self':value,'type':'leaguematch','date':value.date_updated})

    news.sort(key=lambda item:item['date'], reverse=True)
    context = {'user':user,'news':news}
    return render(request, 'streams.html', context)


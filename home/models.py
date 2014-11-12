# -*- coding: utf-8 -*-

import datetime
import os
import pwd
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.dateformat import format
from django.db.models import Q, Count


class Game(models.Model):
    name = models.TextField()
    is_active = models.IntegerField(default=1)

    def __unicode__(self):
        return u'[%d] %s(active:%d)' %(self.id, self.name, self.is_active)

class UserProfile(models.Model):
    #required by the auth model
    user = models.ForeignKey(User, unique=True)
    user_icon = models.FileField(upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')))

    def get_gamelink(self):
        return GameLink.objects.filter(user=self.user)

    def get_group(self):
        group = get_or_none(GroupMember,user=self.user,is_active=1)
        if group :
            return group.group
        else :
            return None

    def get_icon(self):
        return "/media/%s"%(self.user_icon)

class Tutorial(models.Model):
    user = models.ForeignKey(User, unique=True)
    is_pass1 = models.IntegerField(default=0)

class GlobalCard(models.Model) :
    user = models.ForeignKey(User)
    title = models.TextField()
    con = models.TextField()
    src = models.FileField(upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')))
    focus_x = models.FloatField(default=0.0)
    focus_y = models.FloatField(default=0.0)
    date_updated = models.DateTimeField(auto_now_add=True)

    def set_src(self,request):
        self.src = upload(request)
        self.save()
        return self.src

class PrivateCard(models.Model) :
    user = models.ForeignKey(User)
    contype = models.CharField(max_length=3)
    con = models.TextField()
    date_updated = models.DateTimeField(auto_now_add=True)

class Feed(models.Model):
    ufrom = models.IntegerField(default=0)
    ufromtype = models.CharField(max_length=1)
    uto = models.IntegerField(default=0)
    utotype = models.CharField(max_length=1)
    feedtype = models.IntegerField(default=1)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'[%d] %s%s->%s%s' %(self.id,self.ufrom,self.ufromtype,self.uto,self.utotype)

    def get_uto(self):
        if self.utotype == 'u':
            return get_or_none(User,id=int(self.uto))
        elif self.utotype == 'l':
            return get_or_none(League,id=int(self.uto))

    def get_ufrom(self):
        if self.ufromtype == 'u':
            return get_or_none(User,id=int(self.ufrom))
        elif self.ufromtype == 'l':
            return get_or_none(League,id=int(self.ufrom))

    def get_con(self,contype='txt'):
        return get_or_none(FeedContents,feed=self,contype=contype)

    def get_time_diff(self):
        if self.date_updated:
            now = timezone.localtime(timezone.now())
            timediff = now - self.date_updated
            timediff = timediff.total_seconds()
            if timediff > 259200:
                return self.date_updated.strftime('%Y년 %m월 %d일')
            elif timediff > 86400:
                return str(int(timediff/3600/24))+"일 전"
            elif timediff > 3600:
                return str(int(timediff/3600))+"시간 전"
            elif timediff > 60:
                return str(int(timediff/60))+"분 전"
            else :
                return "방금 전"

class FeedContents(models.Model):
    feed = models.ForeignKey(Feed)
    contype = models.CharField(max_length=3)
    con = models.TextField()

    def __unicode__(self):
        return u'[%d] %s(%s):%s' %(self.id,self.feed,self.contype,self.con)

class FeedReply(models.Model):
    feed = models.ForeignKey(Feed)
    user = models.ForeignKey(User)
    con = models.TextField()
    date_updated = models.DateTimeField(auto_now_add=True)

    def get_time_diff(self):
        if self.date_updated:
            now = timezone.localtime(timezone.now())
            timediff = now - self.date_updated
            timediff = timediff.total_seconds()
            if timediff > 259200:
                return self.date_updated.strftime('%Y년 %m월 %d일')
            elif timediff > 86400:
                return str(int(timediff/3600/24))+"일 전"
            elif timediff > 3600:
                return str(int(timediff/3600))+"시간 전"
            elif timediff > 60:
                return str(int(timediff/60))+"분 전"
            else :
                return "방금 전"

class Contents(models.Model):
    uto = models.IntegerField(default=0)
    utotype = models.CharField(max_length=1)
    ctype = models.CharField(max_length=3)
    con = models.TextField()

class FeedSmile(models.Model):
    feed = models.ForeignKey(Feed)
    user = models.ForeignKey(User)

class FeedCheck(models.Model):
    feed = models.ForeignKey(Feed)
    user = models.ForeignKey(User)

class GameLink(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    name = models.TextField()
    sid = models.IntegerField(default=0)

    def __unicode__(self):
        return u'[%d] %s (%s)' %(self.id, self.user, self.game)

class Notification(models.Model):
    user = models.ForeignKey(User)
    action = models.TextField()
    icon = models.TextField()
    contents = models.TextField()
    link = models.TextField()
    date_read = models.IntegerField(default=-1)
    date_updated = models.DateTimeField(auto_now_add=True)

    def get_time_diff(self):
        if self.date_updated:
            now = timezone.localtime(timezone.now())
            timediff = now - self.date_updated
            timediff = timediff.total_seconds()
            if timediff > 259200:
                return self.date_updated.strftime('%Y년 %m월 %d일')
            elif timediff > 86400:
                return str(int(timediff/3600/24))+"일 전"
            elif timediff > 3600:
                return str(int(timediff/3600))+"시간 전"
            elif timediff > 60:
                return str(int(timediff/60))+"분 전"
            else :
                return "방금 전"

class Group(models.Model):
    name = models.TextField()
    nick = models.TextField()
    leader = models.ForeignKey(User)
    group_icon = models.TextField(default='common.png')
    game = models.ForeignKey(Game)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' %(self.name)

    def get_member(self):
        if self.id:
            return GroupMember.objects.filter(group=self).order_by("order")

    def get_league_history(self):
        lt = LeagueTeam.objects.filter(group=self,round__round=1)
        return lt.count()

class GroupMember(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)
    order = models.IntegerField(default=0)
    is_active = models.IntegerField(default=0)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'[%d] %s (%s)' %(self.id, self.user.username, self.group)

    def get_gamelink(self):
        if self.user:
            return GameLink.objects.get(user=self.user)

class League(models.Model):
    name = models.TextField()
    host = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    poster = models.FileField(upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')))
    concept = models.TextField()
    rule = models.TextField()
    level = models.IntegerField(default=1)
    method = models.IntegerField(default=0)
    start_apply = models.DateTimeField(editable=True)
    end_apply = models.DateTimeField(editable=True)
    min_team = models.IntegerField(default=0)
    max_team = models.IntegerField(default=0)
    date_updated = models.DateTimeField(auto_now_add=True)

    def get_league_match(self,round=None):
        if round :
            return LeagueMatch.objects.filter(team_a__round__league=self,team_a__round__round=round)
        else :
            return LeagueMatch.objects.filter(team_a__round__league=self)

    def get_league_round(self):
        return LeagueRound.objects.filter(league=self, is_finish=1)

    def get_time_diff(self):
        if self.end_apply:
            now = timezone.localtime(timezone.now())
            if self.start_apply > now :
                return -1
            timediff = self.end_apply - now
            timediff = timediff.total_seconds()
            return timediff

    def __unicode__(self):
        return u'[%d] %s' %(self.id, self.name)

class LeagueRound(models.Model):
    league = models.ForeignKey(League)
    round = models.IntegerField(default=1)
    start = models.DateTimeField(editable=True)
    end = models.DateTimeField(editable=True)
    bestof = models.IntegerField(default=1)
    is_finish = models.IntegerField(default=0)

    def get_time_diff(self):
        if self.start:
            now = timezone.localtime(timezone.now())
            timediff = self.start - now
            timediff = timediff.total_seconds()
            if timediff < 0 :
                return "경기 끝"
            elif timediff < 60:
                return str(int(timediff))+"초 후"
            elif timediff < 3600:
                return str(int(timediff/60))+"분 후"
            elif timediff < 86400:
                return str(int(timediff/3600))+"시간 후"
            else :
                return str(int(timediff/86400))+"일 후"

    def __unicode__(self):
        return u'[%d] R%d(%s)' %(self.id, self.round, self.league)

class LeagueInfo(models.Model):
    name = models.TextField()
    is_required = models.IntegerField(default=0)

class LeagueTeam(models.Model):
    group = models.ForeignKey(Group)
    round = models.ForeignKey(LeagueRound)
    feasible_time = models.TextField()
    is_complete = models.IntegerField(default=1)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'[%d] %s(League:%s, Round:%d)' %(self.id, self.group.name,self.round.league.name,self.round.round)

class LeagueMatch(models.Model):
    game = models.IntegerField(default=1)
    team_a = models.ForeignKey(LeagueTeam, related_name="note_team_a_group")
    team_b = models.ForeignKey(LeagueTeam, related_name="note_team_b_group")
    host = models.IntegerField(default=0)
    state = models.IntegerField(default=0)
    result = models.TextField()
    date_match = models.DateTimeField()
    date_updated = models.DateTimeField(auto_now_add=True)

    def get_time_diff(self):
        if self.date_updated:
            now = timezone.localtime(timezone.now())
            timediff = self.date_updated - now
            timediff = timediff.total_seconds()
            if timediff < 0 :
                return 0
            elif timediff < 60:
                return str(int(timediff))+"초 후"
            elif timediff < 3600:
                return str(int(timediff/60))+"분 후"
            elif timediff < 86400:
                return str(int(timediff/3600))+"시간 후"
            else :
                return str(int(timediff/86400))+"일 후"

    def __unicode__(self):
        return u'[%d] A:%s,B:%s (%s)' %(self.id, self.team_a,self.team_b,self.date_match)

class LeagueReward(models.Model):
    league = models.ForeignKey(League)
    name = models.TextField()
    con = models.TextField()

class LeagueWish(models.Model):
    league = models.ForeignKey(League)
    user = models.ForeignKey(User)
    date_updated = models.DateTimeField(auto_now_add=True)

class Chatting(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)
    con = models.TextField()
    date_updated = models.DateTimeField(auto_now_add=True)


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def upload(request):
    UPLOAD_DIR = "upload/files_%s/" %(format(timezone.localtime(timezone.now()), u'U'))
    if request.method == 'POST':
        if 'file' in request.FILES:
            if not os.path.exists(UPLOAD_DIR):
                os.makedirs(UPLOAD_DIR)
                uid, gid =  pwd.getpwnam('root').pw_uid, pwd.getpwnam('root').pw_uid
                os.chown(UPLOAD_DIR, uid, gid)
            file = request.FILES['file']
            filename = file._name

            fp = open('redbomba/%s/%s' % (UPLOAD_DIR, filename) , 'wb')
            for chunk in file.chunks():
                fp.write(chunk)
            fp.close()
            return "/%s/%s"%(UPLOAD_DIR, filename)
    return None
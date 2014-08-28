# -*- coding: utf-8 -*-

import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Game(models.Model):
  name = models.TextField()
  is_active = models.IntegerField(default=1)

  def __unicode__(self):
    return u'[%d] %s(active:%d)' %(self.id, self.name, self.is_active)

class UserProfile(models.Model):
  #required by the auth model
  user = models.ForeignKey(User, unique=True)
  user_icon = models.IntegerField(default=1)

class Tutorial(models.Model):
  uid = models.ForeignKey(User, unique=True)
  is_pass1 = models.IntegerField(default=0)
 
class Feed(models.Model):
  ufrom = models.IntegerField(default=0)
  ufromtype = models.CharField(max_length=1)
  uto = models.IntegerField(default=0)
  utotype = models.CharField(max_length=1)
  feedtype = models.IntegerField(default=1)
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

  def __unicode__(self):
    return u'[%d] %s%s>%s%s' %(self.id,self.ufrom,self.ufromtype,self.uto,self.utotype)
  
class Reply(models.Model):
  date_updated = models.DateTimeField(auto_now_add=True)
  ufrom = models.ForeignKey(User)
  fid = models.ForeignKey(Feed)
  
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
  
class Smile(models.Model):
  fid = models.ForeignKey(Feed)
  uid = models.ForeignKey(User)
  
class Check(models.Model):
  uid = models.ForeignKey(User)
  fid = models.ForeignKey(Feed)

class GameLink(models.Model):
  uid = models.ForeignKey(User)
  game = models.ForeignKey(Game)
  name = models.TextField()
  sid = models.IntegerField(default=0)

  def __unicode__(self):
    return u'[%d] %s (%s)' %(self.id, self.uid, self.game)
  
class Notification(models.Model):
  uid = models.ForeignKey(User)
  tablename = models.TextField()
  contents = models.TextField()
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
  uid = models.ForeignKey(User)
  group_icon = models.TextField(default='common.jpg')
  game = models.ForeignKey(Game)
  date_updated = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return u'%s' %(self.name)

  def get_member(self):
    if self.id:
      return GroupMember.objects.filter(gid=self).order_by("order")
  
class GroupMember(models.Model):
  gid = models.ForeignKey(Group)
  uid = models.ForeignKey(User)
  order = models.IntegerField(default=0)
  is_active = models.IntegerField(default=0)
  date_updated = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return u'[%d] %s (%s)' %(self.id, self.uid.username, self.gid)

  def get_gamelink(self):
    if self.uid:
      return GameLink.objects.get(uid=self.uid)
  
class League(models.Model):
  name = models.TextField()
  uid = models.ForeignKey(User)
  game = models.ForeignKey(Game)
  level = models.IntegerField(default=1)
  method = models.IntegerField(default=0)
  start_apply = models.DateTimeField(editable=True)
  end_apply = models.DateTimeField(editable=True)
  min_team = models.IntegerField(default=0)
  max_team = models.IntegerField(default=0)
  date_updated = models.DateTimeField(auto_now_add=True)

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
  league_id = models.ForeignKey(League)
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
    return u'[%d] R%d(%s)' %(self.id, self.round, self.league_id)
  
class LeagueInfo(models.Model):
  name = models.TextField()
  is_required = models.IntegerField(default=0)
  
class LeagueTeam(models.Model):
  group_id = models.ForeignKey(Group)
  round = models.ForeignKey(LeagueRound)
  feasible_time = models.TextField()
  date_updated = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return u'[%d] %s(League:%s, Round:%d)' %(self.id, self.group_id.name,self.round.league_id.name,self.round.round)
  
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
  league_id = models.ForeignKey(League)
  name = models.TextField()
  con = models.TextField()

class Chatting(models.Model):
  gid = models.ForeignKey(Group)
  uid = models.ForeignKey(User)
  con = models.TextField()
  date_updated = models.DateTimeField(auto_now_add=True)
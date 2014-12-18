# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from django.db import models

# Create your models here.
from django.utils import timezone
from django.utils.dateformat import format
from redbomba.home.models import Game

class ArenaBanner(models.Model):
    src = models.FileField(upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')))
    url = models.TextField(default='/')

METHOD_IN_ARENACARD_CHOICES = (
    (0, '온라인'),
    (1, '오프라인'),
)

class League(models.Model):
    name = models.TextField()
    host = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    poster = models.FileField(upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')))
    concept = models.TextField()
    rule = models.TextField()
    method = models.IntegerField(default=0,choices=METHOD_IN_ARENACARD_CHOICES)
    start_apply = models.DateTimeField(editable=True)
    end_apply = models.DateTimeField(editable=True)
    min_team = models.IntegerField(default=0)
    max_team = models.IntegerField(default=0)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '[%d] %s' %(self.id, self.name)

class LeagueRound(models.Model):
    league = models.ForeignKey(League)
    round = models.IntegerField(default=1)
    start = models.DateTimeField(editable=True)
    end = models.DateTimeField(editable=True)
    bestof = models.IntegerField(default=1)
    is_finish = models.IntegerField(default=0)

    def __unicode__(self):
        return '[%d] R%d(%s)' %(self.id, self.round, self.league)

class LeagueTeam(models.Model):
    group = models.ForeignKey(Group)
    round = models.ForeignKey(LeagueRound)
    feasible_time = models.TextField()
    is_complete = models.IntegerField(default=1)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '[%d] %s(League:%s, Round:%d)' %(self.id, self.group.name,self.round.league.name,self.round.round)

class LeagueMatch(models.Model):
    game = models.IntegerField(default=1)
    team_a = models.ForeignKey(LeagueTeam, related_name="note_team_a_group")
    team_b = models.ForeignKey(LeagueTeam, related_name="note_team_b_group")
    host = models.IntegerField(default=0)
    state = models.IntegerField(default=0)
    result = models.TextField()
    date_match = models.DateTimeField()
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '[%d] A:%s,B:%s (%s)' %(self.id, self.team_a,self.team_b,self.date_match)

class LeagueReward(models.Model):
    league = models.ForeignKey(League)
    name = models.TextField()
    con = models.TextField()

class LeagueWish(models.Model):
    league = models.ForeignKey(League)
    user = models.ForeignKey(User)
    date_updated = models.DateTimeField(auto_now_add=True)